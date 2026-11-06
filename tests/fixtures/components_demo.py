"""Runnable component gallery; all plotted positions are illustrative pixel geometry."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from scientific_components import Figure


def example():
    f=Figure(1000,660)
    f.text('title',35,20,930,'Reusable scientific components',32,bold=True)
    f.chain('pipeline',40,90,['Input','Encoder','Prediction'],150,56,gap=48,fontSize=21,radius=9)
    f.stack('features',760,95,72,60,layers=4,dx=8,dy=-7)
    f.text('features-label',730,169,180,'Feature maps',18,anchor='middle')
    f.text('matrix-label',40,215,175,'Matrix cells',20)
    f.matrix('matrix',40,250,4,5,24,20,colors=['#CDE3EF','#85B4C9','#D9EBDA','#B2D1B1','#F3DCA5']*4,gap=2)
    f.axes('histogram',(260,340),420,235)
    f.bars('bars',274,340,[18,39,73,55,27],barW=18,gap=10)
    f.text('bar-label',270,350,160,'Source-pixel bars',18)
    f.axes('scatter',(480,340),645,235)
    f.scatter('points',[(500,280),(520,295),(533,255),(563,310),(590,268),(620,297)],stroke='#B54869')
    f.text('scatter-label',490,350,155,'Editable points',18)
    f.boxplot('boxplot',735,240,267,288,307,336,w=22)
    f.cycle('recycle',870,290,27)
    f.text('cycle-label',817,350,132,'Cycle arrows',18)
    f.text('math-title',40,413,900,'Explicit math layout; native text, no font fitting',22)
    f.fraction('fraction',65,479,76,[{'text':'x','italic':True},{'text':'2','fontSize':14,'baselineShift':'super'}],'n + 1',fontSize=24)
    f.summation('sum',215,486,63,'N','i = 1',fontSize=40,limitSize=16)
    f.text('math-runs',315,499,250,runs=[{'text':'L','italic':True},{'text':'cls','fontSize':15,'baselineShift':'sub'},{'text':' + λL','italic':True},{'text':'box','fontSize':15,'baselineShift':'sub'}],fontSize=25)
    f.arrow('routed',(610,490),(850,550),via=[(730,490),(730,550)],stroke='#42799A')
    f.text('route-label',590,570,340,'Source routing stays explicit',18,anchor='middle')
    f.notes=['Original component demonstration. Bars, dots and boxplots use illustrative source-pixel coordinates, not scientific measurements.']
    return f


if __name__=='__main__':
    path=example().save(sys.argv[1] if len(sys.argv)>1 else 'build/components.scene.json')
    print(path)
