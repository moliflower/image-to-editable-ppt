"""RepoMaster Figure 1: native redraw against the user-supplied raster.

The paper caption is excluded. Complex logos/mascots remain explicit crops.
No PDF/source vector or OCR data is used to generate the scene.
"""
from pathlib import Path
import math
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from scientific_components import Figure


def example():
    f=Figure(1224,812)
    blue='#5478CB'; navy='#3E58A0'; cream='#F5F4E3'; green='#A9CE8D'
    purple='#9D66A7'; dark='#17213A'
    def text(id,x,y,w,s,size=23,**style):
        return f.text(id,x,y,w,s,size,**style)
    def center(id,x,y,w,s,size=23,**style):
        return text(id,x,y,w,s,size,anchor='middle',**style)
    def arrow(id,a,b,via=(),color=blue,width=3.5,**style):
        return f.arrow(id,a,b,via=via,stroke=color,strokeWidth=width,**style)
    def crop(id,x,y,w,h,purpose='complex-artwork',description='Decorative icon from the RepoMaster reference'):
        f.image_crop(id,x,y,w,h,dict(x=x,y=y,w=w,h=h),purpose=purpose,description=description)
    def dots(id,x,y,n=3,gap=9,r=2.2):
        for i in range(n):f.circle(f'{id}-{i}',x+i*gap,y,r,'#000000','none')
    def bubble(id,x,y,w,h):
        f.path(id,f'M {x+12} {y} L {x+w-12} {y} Q {x+w} {y} {x+w} {y+12} L {x+w} {y+h-10} Q {x+w} {y+h} {x+w-12} {y+h} L {x+92} {y+h} L {x+53} {y+h+21} L {x+42} {y+h} L {x+12} {y+h} Q {x} {y+h} {x} {y+h-12} L {x} {y+12} Q {x} {y} {x+12} {y} Z',fill='#E5F0D9',stroke='#ACD38E',strokeWidth=4)
        center(id+'-text',x+9,y+6,w-18,'“I want to remove scratches\nfrom this old image.”',21,bold=True,fill='#818181')
    def dashbox(id,x,y,w,h,fill=cream,radius=22,stroke='#1A1A1A'):
        f.rect(id,x,y,w,h,fill,stroke,strokeWidth=1.5,dash=[4,2],radius=radius)
    def star(id,cx,cy,r,color):
        p=[]
        for i in range(10):
            a=math.radians(-90+i*36); rr=r if i%2==0 else r*.47
            p.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
        f.polygon(id,p,color,'none')
    def tree(id,x,y,s=1,highlights=False):
        def pt(a,b):return (x+a*s,y+b*s)
        routes=[[(70,10),(70,20)],[(40,20),(100,20)],[(40,20),(40,30)],[(70,20),(70,30)],[(100,20),(100,30)],[(40,35),(40,46)],[(8,46),(75,46)],[(8,46),(8,55)],[(42,46),(42,55)],[(75,46),(75,55)],[(75,60),(75,70)],[(56,70),(82,70)],[(56,70),(56,78)],[(69,70),(69,78)],[(82,70),(82,78)]]
        for i,(a,b) in enumerate(routes):f.line(f'{id}-edge-{i}',pt(*a),pt(*b),'#86A6DC',2*s)
        nodes=[(70,5,20,9,'#747474'),(40,30,21,10,'#8EACE1'),(70,30,21,10,'#8EACE1'),(100,30,21,10,'#8EACE1'),(8,55,22,9,'#35AC1A'),(42,55,22,9,'#35AC1A'),(75,55,22,9,'#35AC1A'),(56,78,8,9,'#4B67FF'),(69,78,8,9,'#4B67FF'),(82,78,8,9,'#4B67FF')]
        for i,(nx,ny,w,h,c) in enumerate(nodes):
            stroke='#B25200' if highlights and i in [1,5,6,8] else 'none'
            f.rect(f'{id}-node-{i}',x+(nx-w/2)*s,y+(ny-h/2)*s,w*s,h*s,c,stroke,strokeWidth=1.5*s,radius=2*s)
        dots(id+'-ellipsis',x+96*s,y+54*s,r=1.8*s,gap=6*s)
    def graph(id,points,edges,colors,radii,edgecolor='#29464C',width=2.5):
        for i,(a,b) in enumerate(edges):f.line(f'{id}-edge-{i}',points[a],points[b],edgecolor,width)
        for i,((x,y),c,r) in enumerate(zip(points,colors,radii)):
            f.circle(f'{id}-node-{i}',x,y,r,c,'#2D4B55' if edgecolor!='#DAB51F' else c,strokeWidth=2.5 if r>6 else 1)
    def ygraph(id,x,y,step=30):
        graph(id,[(x,y),(x-step/2,y+25),(x+step/2,y+25)],[(0,1),(0,2)],['#EF923F','#36AF1C','#36AF1C'],[7,7,7],edgecolor='#111111',width=1.5)

    # Flat section backgrounds and long routes.
    f.rect('repository-analysis-panel',47,16,1129,365,'#F0F6FB',navy,strokeWidth=3.4,radius=33)
    f.rect('execution-background',45,393,515,411,'#F5F0FA')
    f.rect('exploration-background',560,391,618,414,'#EBF8F0')
    f.line('stage-divider',(559,22),(559,360),blue,2.2,dash=[9,8])
    f.path('core-components-brace','M 580 258 Q 584 276 629 274 Q 666 278 714 274 Q 752 272 763 275 Q 800 275 806 295 Q 813 274 850 274 Q 890 278 940 274 L 1008 274 Q 1047 274 1053 254',stroke=blue,strokeWidth=3.3)
    arrow('search-and-select',(231,223),(450,223),width=4)
    arrow('extract-intent',(248,109),(206,109),width=4)
    arrow('lower-query-to-agent',(106,481),(106,515),width=4)
    arrow('initial-to-agent',(262,532),(225,532),width=4)
    arrow('tools-to-tree',(791,522),(734,619),via=[(734,522)],width=3.5)
    arrow('expand-search-scope',(825,676),(1008,676),width=3.5)
    # Large native titles retain the source's handwritten style approximately.
    text('title-search',166,12,381,'(1) Repository Search',40,fontFamily='Gabriola',bold=True)
    text('title-analysis',624,12,513,'(2) Hierarchical Repository Analysis',40,fontFamily='Gabriola',bold=True)
    text('title-exploration',344,402,735,'(3) Autonomous Exploration & Execution',42,fontFamily='Gabriola',bold=True)

    # Repository search panel.
    f.path('intent-note','M 59 75 Q 129 77 194 75 L 193 133 Q 126 131 59 133 Z',fill='#E0E7F5',stroke='#B6C7E9',strokeWidth=3)
    text('intent-label',69,82,120,'# user’s intent\n# key entities',19)
    text('extract-label',205,79,84,'Extract',23)
    bubble('query',278,73,258,54)
    dashbox('repository-pool',60,155,155,220,fill='#F0F6FB',radius=29,stroke='#293E6C')
    # Eight individual GitHub logos, two mascot artworks and small decorative icons.
    for i,(x,y,w,h) in enumerate([(143,168,56,54),(73,229,55,54),(144,230,54,53),(71,305,57,55),(143,304,56,56),(465,166,57,56),(465,230,57,56),(466,296,56,56)]):
        crop(f'github-logo-{i+1}',x,y,w,h,'logo','GitHub mark from the source figure')
    crop('search-magnifier',48,143,70,61)
    arrow('intent-to-search',(122,137),(122,176),width=4)
    dots('pool-top-ellipsis',89,199,gap=13,r=4)
    dots('pool-bottom-ellipsis',117,306,gap=13,r=3.8)
    f.rect('selected-repositories',457,140,76,222,'none','#1C315C',strokeWidth=2.3)
    f.circle('selected-check',472,159,11,'#36C244','none')
    f.path('selected-tick','M 466 158 L 471 163 L 479 154',stroke='#FFFFFF',strokeWidth=2.3)
    f.path('user-head','M 310 152 A 10 10 0 1 0 310 163',stroke='#555555',strokeWidth=3)
    f.circle('user-dot',315,151,2,'#555555','none')
    f.path('user-shoulders','M 285 188 L 285 184 Q 285 173 299 173 L 304 173 Q 319 173 319 185 L 319 188',stroke='#555555',strokeWidth=3)
    center('search-select-label',245,197,204,'Search and Select',23)
    f.path('repository-metadata','M 244 248 Q 284 244 326 248 Q 369 244 419 248 Q 442 250 443 271 L 443 332 Q 442 353 421 353 L 246 353 Q 225 353 225 333 L 225 270 Q 225 249 244 248 Z',fill='#DFE4F4',stroke='#B5C5E8',strokeWidth=3.5)
    # Folded README page with native cells; small smile/sun is native geometry.
    f.path('readme-page','M 266 261 L 308 261 L 308 296 L 294 309 L 266 309 Z',fill='#ECEBE6',stroke='#F4D784',strokeWidth=5)
    f.path('readme-page-fold','M 294 309 L 294 296 L 308 296',stroke='#F4D784',strokeWidth=4)
    f.rect('readme-page-header',274,273,26,4,'#CBD1DB')
    for i in range(4):f.rect(f'readme-page-cell-{i}',274+(i%2)*15,283+(i//2)*10,9,5,'#CBD1DB')
    f.circle('readme-sun',246,265,11,'none','#FF6521',strokeWidth=2)
    f.path('readme-smile','M 240 266 Q 246 273 251 266',stroke='#FF6521',strokeWidth=1.5)
    f.circle('readme-eye-1',241,262,1.2,'#FF6521','none');f.circle('readme-eye-2',250,262,1.2,'#FF6521','none')
    for i in range(8):
        a=math.radians(i*45)
        f.line(f'readme-ray-{i}',(246+14*math.cos(a),265+14*math.sin(a)),(246+18*math.cos(a),265+18*math.sin(a)),'#FF6521',1.7)
    star('repository-star',284,334,21,'#F9BE55')
    text('readme-label',320,270,116,'README file',20)
    text('star-label',321,315,115,'Star number',20)

    # Three structural views and their shared core-component output.
    for id,x,w in [('hierarchy-box',580,146),('dependency-box',744,146),('function-box',908,136)]:dashbox(id,x,81,w,183)
    tree('hierarchical-code-tree',587,97,.99)
    dots('tree-continuation',677,190,n=6,gap=6,r=1.8)
    center('hierarchy-label',588,190,130,'Hierarchical\nCode Tree\n(HCT)',21)
    mdg=[(787,111),(841,111),(805,138),(839,138),(787,171),(818,160),(850,174)]
    graph('module-dependency',mdg,[(0,1),(0,2),(1,2),(2,4),(4,6),(2,5)],['#BBD6E6','#BBD6E6','#E99543','#718F9F','#BBD6E6','#BBD6E6','#E99543'],[8,8,8,8,8,8,8])
    for i in range(3):f.circle(f'dependency-ellipsis-{i}',786,131+i*5,1.2,dark,'none')
    center('dependency-label',750,185,134,'Module\nDependency\nGraph (MDG)',21)
    fcg=[(976,107),(1011,114),(956,129),(980,143),(947,151),(947,174),(980,167),(1008,172),(1014,145)]
    graph('function-call',fcg,[(0,1),(1,2),(1,3),(2,4),(3,4),(3,5),(3,6),(3,7),(1,8)],['#4146F4']*9,[6,8,7,13,7,6,5,6,5],edgecolor='#DAB51F',width=3)
    center('function-label',912,194,128,'Function Call\nGraph (FCG)',21)
    crop('mascot-preparing',1044,74,130,140)
    center('mascot-preparing-label',1042,220,132,'RepoMaster',24,bold=True)
    f.polygon('preparing-bookmark',[(1055,276),(1074,276),(1074,303),(1064,294),(1055,303)],'#3896D9','none')
    text('preparing-label',1078,275,100,'preparing',21,bold=True)
    for i in range(9):
        a=math.radians(-90+i*40);r=8-i*.62
        f.circle(f'preparing-spinner-{i}',1101+25*math.cos(a),348+25*math.sin(a),r,'#3A98DD','none')
    f.rect('core-components-band',617,303,415,62,'#FFF4CC','#FFCA00',strokeWidth=3,radius=11)
    f.rect('core-components-inset',620,306,409,56,'none','#FFC900',strokeWidth=.7,radius=8)
    ygraph('core-components-a',653,320);ygraph('core-components-b',763,321,32)
    dots('core-ellipsis',701,347,gap=7,r=2)
    text('core-components-label',799,324,226,'Core components (file, class)',19)
    f.polygon('stage-transition',[(544,359),(573,359),(573,386),(581,386),(558,409),(535,386),(544,386)],'#5678C4','#1B2B58',strokeWidth=1.5)

    # Autonomous agent / execution feedback.
    bubble('query-repeat',69,420,258,54)
    f.rect('agent-panel',56,520,168,96,'#F5F0FA','#AEAEAE',strokeWidth=2.2)
    f.rect('agent-robot',67,537,32,28,'#85C6E5',radius=3)
    f.circle('agent-eye-1',77,546,2.2,'#FFFFFF','none');f.circle('agent-eye-2',89,546,2.2,'#FFFFFF','none')
    f.line('agent-antenna',(83,537),(83,532),'#9DB8C8',2);f.circle('agent-antenna-dot',83,532,2.5,'#9DB8C8','none')
    text('agent-title',107,532,110,'Agent',30,bold=True)
    text('agent-action',61,579,162,'produce new action',20,runs=[{'text':'produce new '},{'text':'action','underline':True}])
    dashbox('initial-components',252,498,152,91,radius=20)
    graph('initial-components-graph',[(321,518),(350,517),(331,547),(366,547)],[(0,2),(1,2),(1,3)],['#EF923F','#EF923F','#36AF1C','#36AF1C'],[8]*4,edgecolor='#111111',width=1.5)
    dots('initial-ellipsis',372,521,gap=7,r=2)
    text('initial-components-label',268,533,100,'Initial\ncomponents',18)
    f.rect('explore-repo-box',87,627,149,29,'#D3E4B6','#79AD3E',strokeWidth=2,dash=[5,4],radius=3)
    center('explore-repo-label',88,629,148,'Explore the Repo',21,bold=True)
    f.path('agent-explore-loop','M 79 618 C 52 616 48 647 72 653 L 73 645 L 79 656 L 70 667 L 70 660 C 43 650 53 623 79 627 Z',fill='#577BC4',stroke='#2B3C6C',strokeWidth=1.5)
    f.path('feedback-to-agent','M 263 675 C 291 652 281 624 247 617 L 249 625 L 236 616 L 244 604 L 244 611 C 288 619 298 652 270 679 Z',fill='#577BC4',stroke='#2B3C6C',strokeWidth=1.5)
    f.rect('action-observation-band',50,672,377,67,'#A3C4E7','#AFAFAF',strokeWidth=2)
    f.rect('feedback-band',50,739,377,62,'#9D7EB7','#AFAFAF',strokeWidth=2)
    center('action-observation-label',62,691,353,'Actions → Observations',29,bold=True,fill='#FFFFFF')
    center('feedback-label',58,752,362,'Analyse Feedback & Optimize',27,fill='#FFFFFF')

    # Native circular workflow with independently editable curved lettering.
    f.circle('mascot-disc',559,595,88,'#DEECFF','none')
    f.path('exploration-semicircle','M 562 470 A 126 126 0 0 1 562 722',stroke='#ABC96D',strokeWidth=15)
    f.path('execution-semicircle','M 555 722 A 126 126 0 0 1 555 470',stroke=purple,strokeWidth=15)
    f.polygon('exploration-arrowhead',[(563,714),(551,722),(564,730)],'#ABC96D','none')
    f.polygon('execution-arrowhead',[(554,462),(566,470),(554,478)],purple,'none')
    f.path('exploration-arrow-notch','M 691 592 L 698 599 L 706 593',stroke='#FFFFFF',strokeWidth=1)
    f.path('execution-arrow-notch','M 412 592 L 419 599 L 427 593',stroke='#FFFFFF',strokeWidth=1)
    def arc_label(id,label,start,end,r=106):
        for i,char in enumerate(label):
            a=start+(end-start)*i/(len(label)-1)
            x=559+r*math.cos(math.radians(a));y=595+r*math.sin(math.radians(a))
            center(f'{id}-{i}',x-14,y-19,28,char,29,rotation=a+90)
    arc_label('execution-label','Execution',148,213)
    arc_label('exploration-label','Exploration',-45,35)
    crop('mascot-exploring',482,526,145,114)
    center('mascot-exploring-label',478,641,164,'RepoMaster',27,bold=True)

    # Exploration tools. Text, tool letters and their connections stay native.
    f.rect('tools-icon-background',793,457,119,118,'#E0E9FB')
    for id,y,c in [('code-view',455,'#F7D331'),('dependency-analysis',493,'#F35F61'),('tool-search',532,'#96ABDC')]:f.rect(id+'-band',909,y,251,38,c)
    # Folder, magnifying glass and split routes.
    f.rect('tool-folder',800,469,48,37,'#F4BD83','#161616',strokeWidth=3,radius=3)
    f.line('folder-tab-left',(815,469),(815,482),'#161616',2.5);f.line('folder-tab-right',(832,469),(832,482),'#161616',2.5)
    f.circle('tool-magnifier-outer',824,514,27,'#EADCC6','#111111',strokeWidth=3)
    f.circle('tool-magnifier-inner',824,514,19,'#E8F3F0','#111111',strokeWidth=3)
    f.line('tool-magnifier-stripe',(806,516),(841,516),'#577E8E',3)
    f.rect('tool-magnifier-handle',819,540,10,16,'#FFFFFF','#111111',strokeWidth=2)
    f.rect('tool-magnifier-tip',817,556,14,15,'#EF6570','#111111',strokeWidth=2)
    arrow('tool-to-a',(849,511),(879,482),color='#111111',width=2.5)
    arrow('tool-to-b',(852,516),(875,516),color='#111111',width=2.5)
    arrow('tool-to-c',(849,523),(879,545),color='#111111',width=2.5)
    for letter,y,c in [('A',477,'#FBE248'),('B',515,'#EE666A'),('C',553,'#4E7CD0')]:
        f.circle('tool-'+letter,891,y,15,c,'#111111',strokeWidth=3)
        center('tool-'+letter+'-label',879,y-15,24,letter,26,bold=True,fontFamily='Arial')
    text('granular-code-label',922,460,225,'Granular Code View',23)
    text('dependency-analysis-label',922,499,195,'Dependency Analysis',22)
    text('search-tool-label',923,536,150,'Search',23)
    for id,x,y,w,h in [('code-view-icon',1121,457,38,36),('dependency-icon',1121,495,38,35),('search-tool-icon',1121,533,39,36)]:crop(id,x,y,w,h)
    text('exploration-tools-label',803,575,249,'Exploration tools',24)

    # Progressive exploration: trees, search/trace tools and expanded scope.
    dashbox('initial-tree-box',707,621,116,94,radius=19)
    tree('initial-code-tree',712,623,.86,highlights=True)
    f.rect('search-action-box',839,622,147,42,'#D2E4B8','#7FAF42',strokeWidth=2,dash=[5,5],radius=9)
    crop('search-action-icon',844,626,45,35)
    text('search-action-label',892,629,88,'Search',22)
    f.rect('trace-action-box',837,683,167,45,'#D2E4B8','#7FAF42',strokeWidth=2,dash=[5,5],radius=4)
    f.path('trace-shape','M 844 685 L 851 688 L 858 685 L 858 693 L 865 693 Q 880 691 880 700 L 880 704 L 849 704 Q 843 704 844 711 L 844 715 L 879 715 L 879 721',stroke='#1C2F20',strokeWidth=2.2)
    arrow('trace-arrow',(848,721),(879,721),color='#1C2F20',width=1.7)
    text('trace-action-label',886,690,55,'Trace',21)
    small=[(939,691),(956,692),(945,702),(936,714),(956,714)]
    graph('trace-mdg',small,[(0,1),(0,2),(1,2),(2,3),(3,4)],['#B7D6E6','#B7D6E6','#E9A053','#B7D6E6','#B7D6E6'],[3.3]*5,width=1)
    small=[(977,692),(990,695),(972,704),(984,707),(992,718),(975,717)]
    graph('trace-fcg',small,[(0,1),(1,2),(1,3),(2,3),(3,4),(3,5)],['#4449F6']*6,[3.3,3.3,3.3,5,3.3,3.3],edgecolor='#DAB51F',width=1.3)
    dashbox('expanded-tree-box',1017,612,153,120,radius=21)
    tree('expanded-code-tree',1027,626,.97,highlights=True)
    dots('expanded-tree-ellipsis',1137,634,gap=6,r=1.8)
    crop('expanded-view-icon',1130,674,38,36)
    text('expanded-view-label',1127,705,44,'view',20)
    center('expanded-scope-label',944,747,230,'Expand viewed scope',23)
    f.rect('iterative-optimize-box',611,746,226,36,'#F5F0FA','#A483BE',strokeWidth=2,dash=[6,5],radius=6)
    center('iterative-optimize-label',614,748,220,'Iteratively optimize',26)
    f.path('iterate-back-arrow','M 898 733 C 924 769 907 795 865 778 L 854 783 L 855 765 L 875 770 L 868 774 C 899 787 913 767 891 737 Z',fill='#577BC4',stroke='#263C68',strokeWidth=1.6)
    f.notes=[
        'Adaptation of RepoMaster Figure 1 (Wang et al., NeurIPS 2025); see SOURCE.md for attribution and rights.',
        'Authored from the user-supplied PNG, cropped only to exclude the paper caption. No PDF vectors or source text objects were imported.',
        'Complex GitHub logos, mascots and decorative tool icons remain declared raster crops. Diagram labels, trees, graphs, shapes and arrows are native objects.',
        'Handwritten headings use installed Gabriola as an approximation. Circular workflow lettering uses independently editable rotated characters.',
        'Freehand borders, minor decorative symbols and arrow curvature are approximate; section order and principal routes are retained.'
    ]
    return f


if __name__=='__main__':
    print(example().save(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('scene.json')))
