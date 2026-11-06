#!/usr/bin/env python3
"""Record wall-clock reconstruction time, including finding/inspecting the source."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def write(path, data):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data


def start(path, label):
    if Path(path).exists():
        raise ValueError("Session already exists; do not reset the clock to hide earlier work")
    return write(path,{'label':label,'startedAt':now(),'status':'active','events':[],
                       'scope':'Source acquisition, inspection, scene authoring, build, visual review and delivery preparation. Excludes prior tool development and subsequent chat rendering.'})


def mark(path, label):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    if data['status'] != 'active':
        raise ValueError("Session already finished")
    data['events'].append({'label':label,'at':now()})
    return write(path,data)


def finish(path, build_report, review):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    if data['status'] != 'active':
        raise ValueError("Session already finished")
    result=json.loads(Path(build_report).read_text(encoding='utf-8'))
    if not review.strip() or not result['auditPassed'] or result['render']['status'] != 'rendered':
        raise ValueError("A passing audit, actual rendered preview and explicit visual-review note are required")
    for filename,expected in [(result['output'],result['render']['pptxSha256']),
                              (result['render']['preview'],result['render']['pngSha256'])]:
        if hashlib.sha256(Path(filename).read_bytes()).hexdigest() != expected:
            raise ValueError("Final artifact changed since its build/render; rebuild and review it")
    end=now()
    elapsed=(datetime.fromisoformat(end)-datetime.fromisoformat(data['startedAt'])).total_seconds()
    if elapsed < 0:
        raise ValueError("Clock moved backwards; cannot report a valid elapsed time")
    data.update(status='complete',completedAt=end,elapsedSeconds=round(elapsed,3),visualReview=review,
                output=result['output'],preview=result['render']['preview'],objectCount=result['objectCount'],
                images=result['images'],buildTimingsSeconds=result['timingsSeconds'])
    return write(path,data)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['start','mark','finish'])
    parser.add_argument('--session',required=True)
    parser.add_argument('--label')
    parser.add_argument('--build-report')
    parser.add_argument('--review')
    args=parser.parse_args()
    if args.action in ('start','mark'):
        if not args.label:
            parser.error('--label is required')
        data=(start if args.action=='start' else mark)(args.session,args.label)
    else:
        if not args.build_report or not args.review:
            parser.error('--build-report and --review are required')
        data=finish(args.session,args.build_report,args.review)
    print(json.dumps({k:data[k] for k in ('label','status','startedAt','completedAt','elapsedSeconds','output') if k in data},ensure_ascii=False))


if __name__=='__main__':
    main()
