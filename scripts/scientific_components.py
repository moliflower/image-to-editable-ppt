"""Small, explicit scientific-figure components that emit the existing scene JSON.

All geometry uses source pixels. Components expand to individually editable
nodes; they do not measure fonts, shrink text, infer data or rasterize diagrams.
"""
import copy
from dataclasses import dataclass
import json
import math
from pathlib import Path


def positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return value


def count(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def palette(value, length):
    if isinstance(value, str):
        return [value] * length
    if len(value) != length:
        raise ValueError("Color list must match the number of elements")
    return list(value)


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float

    def port(self, side):
        return {"left": (self.x, self.y + self.h / 2), "right": (self.x + self.w, self.y + self.h / 2),
                "top": (self.x + self.w / 2, self.y), "bottom": (self.x + self.w / 2, self.y + self.h)}[side]


class Figure:
    def __init__(self, width, height, font="Times New Roman"):
        self.canvas = {"width": positive(width, "width"), "height": positive(height, "height")}
        self.font = font
        self.nodes = []
        self.assets = []
        self.notes = []
        self._ids = set()

    def add(self, id, type, **props):
        if not isinstance(id, str) or not id.strip() or id in self._ids:
            raise ValueError(f"Missing or duplicate ID: {id}")
        self._ids.add(id)
        node = {"id": id, "type": type, **copy.deepcopy(props)}
        self.nodes.append(node)
        return node

    def rect(self, id, x, y, w, h, fill="none", stroke="none", **style):
        return self.add(id, "rect", x=x, y=y, w=positive(w, "w"), h=positive(h, "h"), fill=fill, stroke=stroke, **style)

    def text(self, id, x, y, w, text=None, fontSize=16, h=None, runs=None, **style):
        positive(fontSize, "fontSize")
        if runs is not None:
            combined = "".join(run["text"] for run in runs)
            if text is not None and text != combined:
                raise ValueError("Explicit text must equal concatenated runs")
            text = combined
            style["runs"] = runs
        if not isinstance(text, str) or not text:
            raise ValueError("Text must be nonempty")
        largest = max([fontSize] + [run.get("fontSize", fontSize) for run in runs or []])
        height = h if h is not None else largest * 1.35 * len(text.replace("\r\n", "\n").split("\n"))
        return self.add(id, "text", x=x, y=y, w=positive(w, "w"), h=positive(height, "h"),
                        text=text, fontSize=fontSize, **{"fontFamily": self.font, "fill": "#111111", **style})

    def line(self, id, start, end, stroke="#777777", strokeWidth=1.5, **style):
        return self.add(id, "line", x=start[0], y=start[1], x2=end[0], y2=end[1],
                        stroke=stroke, strokeWidth=strokeWidth, **style)

    def path(self, id, d, fill="none", stroke="#777777", strokeWidth=1.5, **style):
        return self.add(id, "path", d=d, fill=fill, stroke=stroke, strokeWidth=strokeWidth, **style)

    def polygon(self, id, points, fill="none", stroke="#777777", **style):
        return self.add(id, "polyline", points=" ".join(f"{x},{y}" for x, y in points), closed=True,
                        fill=fill, stroke=stroke, **style)

    def circle(self, id, cx, cy, r, fill="none", stroke="#777777", **style):
        positive(r, "radius")
        return self.add(id, "ellipse", x=cx-r, y=cy-r, w=2*r, h=2*r, fill=fill, stroke=stroke, **style)

    def arrow(self, id, start, end, via=(), **style):
        if not via:
            return self.line(id, start, end, arrow=True, **style)
        d = "M " + " L ".join(f"{x} {y}" for x, y in [start, *via, end])
        return self.path(id, d, arrow=True, **style)

    def block(self, id, x, y, w, h, label, fontSize=16, fill="#EAF2FA", stroke="#54748F",
              textStyle=None, **shapeStyle):
        self.rect(id, x, y, w, h, fill, stroke, **shapeStyle)
        # Separate label has the same explicit frame; no automatic width/size fitting.
        self.text(id+"-label", x, y, w, label, fontSize, h=h,
                  **{"anchor": "middle", "verticalAlign": "middle", **(textStyle or {})})
        return Box(x, y, w, h)

    def chain(self, id, x, y, labels, w, h, gap=24, vertical=False, arrowStyle=None, **blockStyle):
        positive(gap, "gap")
        boxes = [self.block(f"{id}-{i+1}", x if vertical else x+i*(w+gap),
                            y+i*(h+gap) if vertical else y, w, h, label, **blockStyle)
                 for i, label in enumerate(labels)]
        for i, (a, b) in enumerate(zip(boxes, boxes[1:])):
            self.arrow(f"{id}-arrow-{i+1}", a.port("bottom" if vertical else "right"),
                       b.port("top" if vertical else "left"), **(arrowStyle or {}))
        return boxes

    def stack(self, id, x, y, w, h, layers=3, dx=5, dy=-5, fill="#DDEBFA", stroke="#4080B0", **style):
        count(layers, "layers")
        colors = palette(fill, layers)
        for i in reversed(range(layers)):
            self.rect(f"{id}-{i+1}", x+i*dx, y+i*dy, w, h, colors[i], stroke, **style)
        return Box(x+min(0,(layers-1)*dx), y+min(0,(layers-1)*dy), w+abs((layers-1)*dx), h+abs((layers-1)*dy))

    def matrix(self, id, x, y, rows, cols, cellW, cellH, colors="#E3EEF8", gap=0, stroke="#FFFFFF", **style):
        count(rows, "rows"); count(cols, "cols")
        positive(cellW, "cellW"); positive(cellH, "cellH")
        if gap < 0:
            raise ValueError("Matrix gap cannot be negative")
        colors = palette(colors, rows*cols)
        for r in range(rows):
            for c in range(cols):
                self.rect(f"{id}-r{r+1}-c{c+1}", x+c*(cellW+gap), y+r*(cellH+gap),
                          cellW, cellH, colors[r*cols+c], stroke, **style)
        return Box(x,y,cols*cellW+(cols-1)*gap,rows*cellH+(rows-1)*gap)

    def bars(self, id, x, baseline, heights, barW=6, gap=5, fill="#FFE4B4", stroke="#BB651A", **style):
        positive(barW, "barW")
        if gap < 0 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v < 0 for v in heights):
            raise ValueError("Bar heights and gaps must be finite and nonnegative")
        colors = palette(fill, len(heights))
        for i, value in enumerate(heights):
            if value:
                self.rect(f"{id}-{i+1}", x+i*(barW+gap), baseline-value, barW, value, colors[i], stroke, **style)

    def scatter(self, id, points, r=3, fill="none", stroke="#C33", **style):
        colors = palette(stroke, len(points))
        for i,(x,y) in enumerate(points):
            self.circle(f"{id}-{i+1}", x,y,r,fill,colors[i],**style)

    def axes(self, id, origin, right, top, **style):
        self.arrow(id+"-x", origin, (right,origin[1]), **style)
        self.arrow(id+"-y", origin, (origin[0],top), **style)

    def boxplot(self, id, x, top, q1, median, q3, bottom, w=9, fill="#DCECF8", stroke="#2384BA", **style):
        if not top <= q1 <= median <= q3 <= bottom or q1 == q3:
            raise ValueError("Boxplot source-pixel positions must satisfy top <= q1 <= median <= q3 <= bottom")
        self.line(id+"-whisker",(x,top),(x,bottom),stroke,**style)
        self.line(id+"-upper-cap",(x-w/2,top),(x+w/2,top),stroke,**style)
        self.line(id+"-lower-cap",(x-w/2,bottom),(x+w/2,bottom),stroke,**style)
        self.rect(id+"-box",x-w/2,q1,w,q3-q1,fill,stroke,**style)
        self.line(id+"-median",(x-w/2,median),(x+w/2,median),stroke,**style)

    def cycle(self, id, cx, cy, r, stroke="#C79222", strokeWidth=2):
        positive(r, "radius")
        for i,start in enumerate([-75,105]):
            a,b=math.radians(start),math.radians(start+150)
            d=f"M {cx+r*math.cos(a)} {cy+r*math.sin(a)} A {r} {r} 0 0 1 {cx+r*math.cos(b)} {cy+r*math.sin(b)}"
            self.path(f"{id}-{i+1}",d,stroke=stroke,strokeWidth=strokeWidth,arrow=True)

    def fraction(self, id, x, y, w, numerator, denominator, fontSize=20, gap=3, **style):
        height=fontSize*1.35
        def label(suffix, top, value):
            self.text(id+suffix,x,top,w,value if isinstance(value,str) else None,fontSize,h=height,
                      runs=value if isinstance(value,list) else None,**{"anchor":"middle",**style})
        label("-numerator",y,numerator)
        self.line(id+"-rule",(x,y+height+gap),(x+w,y+height+gap),style.get("fill","#111111"),0.8)
        label("-denominator",y+height+2*gap,denominator)
        return Box(x,y,w,2*height+2*gap)

    def summation(self, id, x, y, w, upper, lower, fontSize=34, limitSize=13, **style):
        # y is the operator text frame top; limits have separate native text boxes.
        self.text(id+"-operator",x,y,w,"∑",fontSize,**{"fontFamily":"Cambria Math","anchor":"middle",**style})
        self.text(id+"-upper",x,y-limitSize*1.35,w,upper,limitSize,**{"anchor":"middle",**style})
        self.text(id+"-lower",x,y+fontSize*1.15,w,lower,limitSize,**{"anchor":"middle",**style})

    def image_crop(self, id, x, y, w, h, crop, purpose="complex-artwork", description=""):
        if set(crop) != {"x","y","w","h"} or any(isinstance(v,bool) or not isinstance(v,int) for v in crop.values()):
            raise ValueError("Crop must contain integer x,y,w,h")
        if crop['x'] < 0 or crop['y'] < 0 or crop['w'] <= 0 or crop['h'] <= 0:
            raise ValueError("Crop must have positive dimensions and nonnegative origin")
        node=self.add(id,"image",x=x,y=y,w=w,h=h,crop=crop,sourceAssetId=id,
                      assetPurpose=purpose,assetDescription=description)
        self.assets.append({"id":id,"crop":copy.deepcopy(crop)})
        return node

    def save(self, path):
        scene={"canvas":self.canvas,"nodes":self.nodes,"reviewNotes":self.notes}
        if self.assets:
            scene["sourceAssets"]=self.assets
        target=Path(path)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return target
