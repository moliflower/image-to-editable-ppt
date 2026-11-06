"""Editable redraw of PosDiffNet Fig. 1, authored against reference.png.

Only the three point-cloud views are source crops. The paper PDF was used to
obtain the clear raster reference, not to import vector paths or text objects.
Run from any directory; requires the repository's normal export dependencies.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scientific_components import Figure


def example():
    f = Figure(1032, 606)
    green, brown, blue, gold = '#548735', '#914000', '#307CBF', '#BE9500'

    def text(id, x, y, w, label, size=18, **style):
        return f.text(id, x, y, w, label, size, bold=True, **style)

    def center(id, x, y, w, label, size=18, **style):
        return text(id, x, y, w, label, size, anchor='middle', **style)

    def block(id, x, y, w, h, label, fill, size=18, radius=12):
        return f.block(id, x, y, w, h, label, fontSize=size, fill=fill,
                       stroke='#A3A3A3', strokeWidth=.8, radius=radius,
                       textStyle={'bold': True, 'fill': '#171717'})

    def arrow(id, start, end, via=(), color=green, width=1.8, **style):
        return f.arrow(id, start, end, via=via, stroke=color, strokeWidth=width, **style)

    def broad(id, x, y, w=18, h=23, color=gold):
        f.polygon(id, [(x,y+h*.26),(x+w*.52,y+h*.26),(x+w*.52,y),
                      (x+w,y+h*.5),(x+w*.52,y+h),(x+w*.52,y+h*.74),(x,y+h*.74)],
                  fill=color, stroke='none')

    def prism(id, x, y, w, h, d, colors):
        front, top, side = colors
        f.rect(id+'-front',x,y,w,h,front)
        f.polygon(id+'-top',[(x,y),(x+d,y-d),(x+w+d,y-d),(x+w,y)],top,'none')
        f.polygon(id+'-side',[(x+w,y),(x+w+d,y-d),(x+w+d,y+h-d),(x+w,y+h)],side,'none')

    colors = {
        'yellow': ('#FFCA00','#FFDA42','#CD9A00'),
        'olive': ('#BD9500','#D1AE31','#977600'),
        'magenta': ('#AB006E','#C44190','#81004D'),
        'purple': ('#9B60BA','#B38ECC','#652D8A'),
        'navy': ('#141174','#423C99','#080146'),
        'orange': ('#FF972A','#FFB65E','#D17823'),
        'peach': ('#F7B185','#F8C8A9','#C88C69'),
        'blue': ('#3196FF','#67B6FF','#1978CF'),
        'violet': ('#6E63FF','#938BFF','#4F4ACC'),
        'slate': ('#B0C4E1','#D0DDF0','#8F9DB8'),
        'pink': ('#F49B9F','#FFB5B8','#C8797C'),
        'rose': ('#FFCBCC','#FFE0DE','#D1AAAE'),
        'lime': ('#ADF018','#CBFF57','#86BB18'),
        'leaf': ('#95D257','#B2E487','#6FA744'),
        'brown': ('#99602B','#B58C5A','#75502C'),
        'teal': ('#008C8B','#39ADAA','#006C6D'),
    }

    def feature(id,x,y,color,w=8,h=31,d=15):
        prism(id,x,y,w,h,d,colors[color])

    def math(id, x, y, base, index='', prime=False, size=18, w=57):
        runs = [{'text': base}]
        if index:
            runs.append({'text': index, 'fontSize': size*.72, 'baselineShift':'super'})
        if prime:
            runs.append({'text':'′','fontSize':size*.75,'baselineShift':'super'})
        f.text(id,x,y,w,runs=runs,fontSize=size,bold=True,h=27)

    # Panel outlines and every long route precede their foreground labels.
    f.rect('embedding-panel',24,328,416,273,'#EDEDED','#2855A3',strokeWidth=1.7,radius=18)
    f.rect('attention-panel',446,334,554,263,'#EDEDED','#2855A3',strokeWidth=1.7,radius=18)
    f.rect('prediction-panel',720,215,279,112,'#DAD5FA','#9796AE',strokeWidth=1,radius=18)
    arrow('downsample-p-to-multiscale',(185,58),(225,47),[(185,47)],width=1.7)
    arrow('downsample-q-to-multiscale',(186,282),(225,306),[(186,306)],width=1.7)
    arrow('p-to-window',(185,130),(185,146))
    arrow('q-to-window',(185,203),(185,188))
    arrow('window-to-upper-scale',(279,137),(279,91))
    arrow('window-to-lower-scale',(279,186),(279,231))
    arrow('upper-feature-to-transformer',(514,89),(594,116),[(594,89)])
    f.path('upper-position-route','M 486 134 L 534 134 L 534 89',stroke=green,strokeWidth=1.8)
    arrow('lower-feature-to-transformer',(516,219),(594,200),[(594,219)])
    f.path('lower-position-route','M 485 188 L 534 188 L 534 219',stroke=green,strokeWidth=1.8)
    arrow('registration-to-result',(888,268),(870,268),color='#171717')

    # Source pixels: point clouds alone, not labels, borders or architecture.
    for name,crop,color in [('point-cloud-p',(9,56,124,88),gold),('point-cloud-q',(9,190,124,87),blue),('registered-point-clouds',(742,224,126,79),'#7030A0')]:
        x,y,w,h=crop
        f.image_crop(name,x,y,w,h,dict(x=x,y=y,w=w,h=h),purpose='complex-artwork',description='Point-cloud visualization from PosDiffNet Figure 1')
        f.rect(name+'-border',x-1,y-1,w+2,h+2,'none',color,strokeWidth=1.7)
    center('p-label',7,149,130,'Point Cloud P',18)
    center('q-label',7,280,130,'Point Cloud Q',18)
    broad('p-input',135,87,w=13,h=24)
    broad('q-input',135,216,w=13,h=24,color=blue)
    block('downsample-p',148,58,74,72,'Down-\nsampling\nModule','#BCC7D8')
    block('downsample-q',148,203,75,80,'Down-\nsampling\nModule','#BCC7D8')
    block('window-embedding',135,145,104,44,'Window\nEmbedding','#F8D9FB',18,7)
    block('multiscale-p',225,4,107,87,'Multi-Scale\nDown-\nsampling\nPoints','#E6E6E6',18,0)
    block('multiscale-q',225,231,107,93,'Multi-Scale\nDown-\nsampling\nPoints','#E6E6E6',18,0)
    block('diffusion-p',350,10,95,88,'Beltrami\nDiffusion\nEmbedding','#D7FFA3')
    block('diffusion-q',350,214,96,92,'Beltrami\nDiffusion\nEmbedding','#D7FFA3')
    for id,x,y,color in [('scale-p',333,40,gold),('scale-q',334,254,blue),('window-p',241,145,gold),('window-q',241,165,blue),('diffusion-p-upper',449,32,gold),('diffusion-p-lower',449,76,gold),('diffusion-q-upper',450,179,blue),('diffusion-q-lower',450,264,blue)]:
        broad(id,x,y,w=17,h=23,color=color)
    palette=['#CCDFAF']*16
    for i,c in {1:'#E4ECC8',5:'#3179AC',6:'#89B262',10:'#C0A000'}.items(): palette[i]=c
    f.matrix('window-similarity',258,138,4,4,10,12,colors=palette,stroke='#111111',strokeWidth=.65)
    center('outlier-filter',289,95,159,'Top-k & Radius\nOutlier Removal',18)
    center('similarity-label',296,160,117,'Window\nSimilarity',18)
    block('feature-position-transformer',539,116,109,85,'Feature-\nPosition\nTransformer','#A9DDFC',18,14)

    # Thin native three-face tensors, including their native superscripts.
    for id,x,y,c in [('u-prime',468,39,'yellow'),('fu-prime',493,39,'magenta'),('u',466,98,'olive'),('fu',481,105,'orange'),('eu',499,89,'peach'),('v',470,198,'blue'),('fv',486,202,'violet'),('ev',502,189,'slate'),('v-prime',471,262,'purple'),('fv-prime',496,262,'navy')]:
        feature(id,x,y,c)
    math('u-prime-label',470,8,'U',prime=True)
    math('fu-prime-label',509,10,'F','U′')
    math('u-label',464,130,'U')
    math('fu-label',489,130,'F','U')
    math('eu-label',513,56,'E','U')
    math('v-label',469,230,'V')
    math('fv-label',501,225,'F','V')
    math('ev-label',501,151,'E','V')
    math('v-prime-label',467,292,'V',prime=True)
    math('fv-prime-label',490,291,'F','V′')
    feature('cross-feature-uv',662,75,'purple',h=45)
    feature('cross-feature-vu',658,209,'teal',h=44)
    for id,x,y,index in [('uv-feature-label',626,26,'U'),('vu-feature-label',622,237,'V')]:
        f.text(id,x,y,96,runs=[{'text':'F'},{'text':index,'fontSize':13,'baselineShift':'super'},{'text':'sc_'+('UV' if index=='U' else 'VU'),'fontSize':14,'baselineShift':'sub'}],fontSize=19,bold=True,h=33)
    for id,d in [('upper-out','M 640 112 L 649 105 L 647 101 L 654 105 L 654 119 L 650 114 L 643 123 Z'),('upper-to-distance','M 681 123 L 690 116 L 687 111 L 695 115 L 699 128 L 688 132 L 692 128 Z'),('lower-out','M 642 192 L 651 202 L 654 198 L 657 212 L 644 216 L 648 211 L 639 201 Z'),('lower-to-distance','M 680 195 L 691 185 L 687 181 L 700 177 L 699 190 L 695 187 L 687 202 Z')]:
        f.path(id,d,fill='#EEEEEE',stroke='#808080',strokeWidth=.8)
    matrix=['#FFF3CC']*42
    for i,c in {8:'#B7D48B',18:'#773099',24:'#FFC900',33:'#D800D7',37:'#C56808'}.items(): matrix[i]=c
    f.matrix('patch-distance',707,100,6,7,10,12,colors=matrix,stroke='#111111',strokeWidth=.65)
    center('distance-label',683,172,146,'Patch Feature\nDistance Matrix',18)
    f.path('top-k-route','M 739 94 L 739 67 L 774 67 L 774 61 L 782 72 L 774 81 L 774 75 L 747 75 L 747 94 Z',fill='#EEEEEE',stroke='#888888',strokeWidth=.8)
    text('top-k-title',732,40,78,'Top-k',18)
    for row,y in enumerate([35,119]):
        feature(f'pair-{row}-magenta',798,y-5,'magenta',h=14)
        feature(f'pair-{row}-navy',800,y+15,'navy',h=14)
        f.path(f'pair-{row}-bracket',f'M 797 {y-12} L 791 {y-12} L 791 {y+29} L 797 {y+29}',stroke='#111111',strokeWidth=1.5)
        broad(f'similarity-{row}-in1',826,y-20,w=13,h=19,color=green)
        broad(f'similarity-{row}-in2',826,y+6,w=13,h=19,color=green)
        palette=['#E0EDF5']*16; palette[10]='#D18A28'
        f.matrix(f'similarity-{row}',844,y-24,4,4,10,12,colors=palette,stroke='#111111',strokeWidth=.65)
        broad(f'similarity-{row}-out',903,y,w=18,h=26,color=green)
        for j in range(2):
            feature(f'matched-{row}-{j}-u',944-j*7,y-5+j*29,'yellow',h=10,d=18)
            feature(f'matched-{row}-{j}-v',957-j*7,y-5+j*29,'purple',h=10,d=18)
        f.path(f'match-{row}-bracket',f'M 987 {y-17} L 991 {y-17} L 991 {y+24} L 987 {y+24}',stroke='#111111',strokeWidth=1.5)
    for x in [807,864,908,960]:
        for i in range(3): f.circle(f'ellipsis-{x}-{i}',x,73+i*10,3.2,'#111111','none')
    center('matched-indices',777,145,58,'(ũ,ṽ)',19,italic=True)
    center('similarity-title',827,145,94,'Similarity',18)
    text('similarity-top-k',890,10,76,'Top-k',18)
    f.path('correspondence-bracket','M 922 150 L 922 156 L 996 156 L 996 150',stroke='#111111',strokeWidth=1.5)
    center('corresponding-points',883,162,144,'Corresponding\nPoints',18)
    f.path('correspondence-to-registration','M 949 201 L 959 201 L 959 209 L 967 209 L 954 221 L 941 209 L 949 209 Z',fill='#EEEEEE',stroke='#888888',strokeWidth=.8)
    block('registration',888,229,103,79,'Registration\nMethods','#FFDC73',18)
    center('prediction-label',723,308,165,'Prediction Results',18)

    # Beltrami embedding inset.
    center('embedding-title',45,330,372,'Beltrami Diffusion Embedding',18)
    f.rect('kpconv-background',83,351,136,115,'#FFF6A4','#B8B18A',strokeWidth=.8,radius=18)
    f.rect('gnn-background',38,471,157,104,'#9EBCEB','#7994B5',strokeWidth=.8,radius=17)
    for i,(x,y,h,d) in enumerate([(95,390,57,30),(110,400,43,23),(125,405,32,16),(140,402,29,13),(154,405,37,20),(170,395,40,33)]):
        prism(f'kpconv-level-{i}',x,y,9,h,d,colors['rose'])
    arrow('kpconv-long-skip',(125,390),(186,382),[(125,361),(186,361)],color=brown,width=1.1)
    arrow('kpconv-short-skip',(141,395),(165,385),[(141,373),(165,373)],color=brown,width=1.1)
    text('input-points',26,392,64,'Input\nPoints',18)
    arrow('input-to-kpconv',(66,414),(83,414),color=brown)
    center('kpconv-label',89,447,126,'KPConv-FPN',18)
    arrow('kpconv-to-states',(223,414),(239,414),color=brown)
    block('beltrami-left',225,454,80,46,'Beltrami\nDiffusion','#9EBCEB',18,8)
    block('beltrami-right',316,454,80,46,'Beltrami\nDiffusion','#9EBCEB',18,8)
    for id,x,y,c in [('i-u',253,380,'pink'),('h-u',253,411,'brown'),('u-embed',280,407,'olive'),('i-up',336,378,'lime'),('h-up',336,410,'magenta'),('up-embed',360,406,'yellow'),('e-u-embed',252,518,'peach'),('f-u-embed',252,551,'orange'),('u-out',283,548,'olive'),('e-up-embed',335,518,'leaf'),('f-up-embed',335,552,'magenta'),('up-out',360,549,'yellow')]:
        feature(id,x,y,c,w=7,h=28,d=17)
    for id,x,y,b,i in [('i-u-label',233,364,'I','U'),('h-u-label',223,425,'H','U'),('i-up-label',311,360,'I','U′'),('h-up-label',312,432,'H','U′'),('e-u-embed-label',228,504,'E','U'),('f-u-embed-label',225,576,'F','U'),('e-up-embed-label',311,504,'E','U′'),('f-up-embed-label',307,576,'F','U′')]: math(id,x,y,b,i)
    for id,x,y,prime in [('u-embed-label',291,431,False),('up-embed-label',369,431,True),('u-out-label',278,578,False),('up-out-label',364,578,True)]: math(id,x,y,'U',prime=prime)
    arrow('u-to-i',(292,389),(278,375),[(292,375)],width=1.8)
    arrow('up-to-i',(373,386),(354,371),[(373,371)],width=1.8)
    arrow('h-to-beltrami',(270,432),(270,450),color=brown)
    arrow('hp-to-beltrami',(347,432),(347,450),color=brown)
    arrow('iteration-down',(404,412),(404,579),color=gold,width=3.5)
    # GNN cube and actual graph edges.
    prism('gnn-cube',63,499,68,54,16,('#FFD16E','#FFDF90','#C8A654'))
    pts=[(74,517),(97,501),(115,519),(98,526),(84,540),(105,542)]
    for i,(a,b) in enumerate([(0,1),(1,2),(0,4),(1,3),(2,3),(3,4),(3,5),(4,5),(2,5)]):
        f.line(f'gnn-edge-{i}',pts[a],pts[b],brown,1.1)
    f.scatter('gnn-node',pts,r=3.8,fill=brown,stroke=brown,strokeWidth=.5)
    text('gnn-label',62,539,54,'GNN',18)
    f.cycle('gnn-loop',126,492,14,stroke=brown,strokeWidth=2)
    arrow('gnn-feed',(49,557),(62,527),[(53,557),(53,527)],color=brown)
    arrow('gnn-residual',(44,558),(149,558),color=brown)
    arrow('gnn-to-add',(136,528),(161,548),[(161,528)],color=brown)
    f.circle('gnn-add',160,557,8,'none',brown,strokeWidth=1.6)
    f.line('gnn-add-vertical',(160,545),(160,569),brown,1.6)
    arrow('gnn-out',(168,557),(189,557),color=brown)
    arrow('gnn-conditioning',(198,485),(223,472),color='#111111',dash=[5,3])

    # Feature-position Transformer inset.
    center('transformer-title',500,339,453,'Feature-Position Transformer',18)
    f.path('transformer-diffusion-cycle','M 885 373 Q 876 358 851 358 L 538 358 Q 500 358 500 397 L 500 533 Q 500 573 539 573 L 858 573 Q 899 573 899 530 L 899 447',stroke=brown,strokeWidth=2,dash=[16,6])
    arrow('transformer-residual',(456,585),(947,585),color=brown,width=2)
    arrow('transformer-in',(478,584),(500,465),[(478,465)],color=brown,width=2)
    arrow('solver-to-add',(899,491),(955,577),[(899,465),(955,465)],color=brown,width=2)
    f.circle('transformer-add',955,585,8,'none',brown,strokeWidth=2)
    f.line('transformer-add-vertical',(955,571),(955,599),brown,1.8)
    arrow('transformer-output',(963,585),(984,585),color=brown,width=2)
    f.rect('self-attention-background',583,370,126,157,'#D4EDBC','#9CAF98',strokeWidth=.8,radius=22)
    f.rect('cross-attention-background',735,383,144,128,'#FBD6D7','#B8A1A3',strokeWidth=.8,radius=22)
    for id,x,y,c in [('attention-eu',534,382,'peach'),('attention-fu',534,420,'orange'),('attention-fv',534,464,'violet'),('attention-ev',534,506,'slate')]:
        feature(id,x,y,c,w=8,h=28,d=16)
    math('attention-eu-label',506,380,'E','U')
    math('attention-fu-label',509,422,'F','U')
    math('attention-fv-label',509,465,'F','V')
    math('attention-ev-label',509,508,'E','V')
    arrow('eu-to-self',(557,396),(582,426),[(566,396),(566,426)],color='#927300',width=1.5)
    arrow('fu-to-self',(557,435),(566,426),[(566,435)],color='#927300',width=1.5)
    arrow('fv-to-self',(558,470),(582,480),[(566,470),(566,480)],color='#000080',width=1.5)
    arrow('ev-to-self',(557,502),(566,480),[(566,502)],color='#000080',width=1.5)

    def plate(id,x,y,w,color,depth=16):
        prism(id,x,y,w,10,depth,colors[color])

    plate('self-u-position',601,408,74,'peach')
    plate('self-u-query',601,394,74,'orange')
    plate('self-u-key',601,435,74,'orange')
    plate('self-v-position',597,478,74,'slate')
    plate('self-v-query',598,465,74,'violet')
    plate('self-v-key',597,506,74,'violet')
    plate('cross-u-position',760,431,74,'peach')
    plate('cross-u-query',760,417,74,'orange')
    plate('cross-v-position',760,488,74,'slate')
    plate('cross-v-key',760,477,74,'violet')
    # Small, explicitly illustrative mesh edges preserve the source motif.
    for name,top,bottom,color in [('self-u',(613,415),(614,428),'#A19B30'),('self-v',(609,486),(610,499),'#35359F'),('cross',(773,439),(774,470),'#D738AE')]:
        for i in range(6):
            for j in [i%6,(i*3+1)%6]:
                f.line(f'{name}-mesh-{i}-{j}',(top[0]+i*10,top[1]),(bottom[0]+j*10,bottom[1]),color,.55)
    arrow('self-u-to-cross-u',(708,425),(735,425),color='#927300',width=1.6)
    arrow('self-u-to-cross-v',(708,425),(735,481),color='#927300',width=1.6)
    arrow('self-v-to-cross-u',(707,481),(735,425),color='#000080',width=1.6)
    arrow('self-v-to-cross-v',(707,481),(735,481),color='#000080',width=1.6)
    center('self-attention-label',578,527,139,'Feature-Point\nSelf-Attention',18)
    center('cross-attention-label',733,515,149,'Feature-Point\nCross Attention',18)
    f.path('diffusion-solver-ring','M 884 394 A 56 56 0 1 1 899 439 L 897 450 L 896 422 L 924 430 L 913 437 A 40 40 0 1 0 900 395 Z',fill='#FFE8A7',stroke=brown,strokeWidth=1.7)
    center('diffusion-solver-label',897,383,86,'Diffusion\nSolver',18)
    f.notes = [
        'Adaptation of PosDiffNet Figure 1 (She et al., AAAI 2024). Source artwork is not covered by the repository MIT license; see SOURCE.md.',
        'Scene manually authored against a raster crop of the public paper. No PDF vectors or text objects imported.',
        'Point-cloud visualizations remain three separate source crops; all labels, feature faces, matrices, modules and routes are native objects.',
        'Small decorative attention-mesh segments and subtle shadows/radii are approximations; scientific labels and major topology are preserved.',
        'Superscripts are native text runs, not Office equation objects. Paths do not automatically reattach to modules.'
    ]
    return f


if __name__ == '__main__':
    output = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('scene.json')
    print(example().save(output))
