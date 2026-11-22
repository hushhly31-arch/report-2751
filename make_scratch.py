import json, hashlib, zipfile, pathlib
out=pathlib.Path('/home/user/genta-report/packages/web/public/downloads'); out.mkdir(parents=True,exist_ok=True)
assets={}
def costume(name,svg,cx,cy):
    data=svg.encode(); md=hashlib.md5(data).hexdigest(); assets[md+'.svg']=data
    return {'name':name,'assetId':md,'dataFormat':'svg','md5ext':md+'.svg','rotationCenterX':cx,'rotationCenterY':cy}
def target(name,stage,cost):
    return {'isStage':stage,'name':name,'variables':{},'lists':{},'broadcasts':{},'blocks':{},'comments':{},'currentCostume':0,'costumes':[cost],'sounds':[],'volume':100,'layerOrder':0 if stage else 1,**({'tempo':60,'videoTransparency':50,'videoState':'on','textToSpeechLanguage':None} if stage else {'visible':True,'x':0,'y':-145,'size':100,'direction':90,'draggable':False,'rotationStyle':'don’t rotate'})}
stage=target('Stage',True,costume('Langit','<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360"><rect width="480" height="360" fill="#eee8ff"/><text x="240" y="45" text-anchor="middle" font-family="sans-serif" font-size="22" fill="#68529c">TANGKAP BINTANG</text><text x="240" y="75" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#68529c">Panah kiri / kanan • Tangkap sebanyak mungkin dalam 30 detik</text><rect y="335" width="480" height="25" fill="#ceff86"/></svg>',240,180))
stage['variables']={'score':['Skor',0],'time':['Waktu',30]}
player=target('Pemain',False,costume('Keranjang','<svg xmlns="http://www.w3.org/2000/svg" width="70" height="30"><path d="M2 2H68L58 28H12Z" fill="#9176ea"/><path d="M4 4H66" stroke="#544080" stroke-width="5"/></svg>',35,15))
star=target('Bintang',False,costume('Bintang','<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><path d="M16 1L20 11L31 12L23 20L26 31L16 25L6 31L9 20L1 12L12 11Z" fill="#ffce43" stroke="#c99b21"/></svg>',16,16))
star['y']=160; star['layerOrder']=2
def b(t,id,op,n=None,p=None,inputs=None,fields=None,top=False):
    t['blocks'][id]={'opcode':op,'next':n,'parent':p,'inputs':inputs or {},'fields':fields or {},'shadow':False,'topLevel':top}
    if top:t['blocks'][id].update(x=50,y=50)
def num(n):return [1,[4,str(n)]]
def var(id):return [3,[12,'Skor' if id=='score' else 'Waktu',id],[4,'0']]
b(stage,'s0','event_whenflagclicked','s1',top=True)
b(stage,'s1','data_setvariableto','s2','s0',{'VALUE':num(0)},{'VARIABLE':['Skor','score']})
b(stage,'s2','data_setvariableto','s3','s1',{'VALUE':num(30)},{'VARIABLE':['Waktu','time']})
b(stage,'s3','control_repeat','s6','s2',{'TIMES':num(30),'SUBSTACK':[2,'s4']})
b(stage,'s4','control_wait','s5','s3',{'DURATION':num(1)})
b(stage,'s5','data_changevariableby',None,'s4',{'VALUE':num(-1)},{'VARIABLE':['Waktu','time']})
b(stage,'s6','control_stop',None,'s3',fields={'STOP_OPTION':['all',None]});stage['blocks']['s6']['mutation']={'tagName':'mutation','children':[],'hasnext':'false'}
b(player,'p0','event_whenflagclicked','p1',top=True)
b(player,'p1','motion_gotoxy','p2','p0',{'X':num(0),'Y':num(-145)})
b(player,'p2','control_forever',None,'p1',{'SUBSTACK':[2,'p3']})
for suffix,key,delta,nxt in [('3','left arrow',-8,'p6'),('6','right arrow',8,None)]:
    root='p'+suffix; cond=root+'key'; menu=cond+'menu'; move=root+'move'
    b(player,root,'control_if',nxt,'p2' if suffix=='3' else 'p3',{'CONDITION':[2,cond],'SUBSTACK':[2,move]})
    b(player,cond,'sensing_keypressed',None,root,{'KEY_OPTION':[1,menu]})
    b(player,menu,'sensing_keyoptions',None,cond,fields={'KEY_OPTION':[key,None]});player['blocks'][menu]['shadow']=True
    b(player,move,'motion_changexby',None,root,{'DX':num(delta)})
b(star,'a0','event_whenflagclicked','a1',top=True)
b(star,'a1','control_forever',None,'a0',{'SUBSTACK':[2,'a2']})
b(star,'a2','motion_gotoxy','a3','a1',{'X':[3,'rand',[4,'0']],'Y':num(165)})
b(star,'rand','operator_random',None,'a2',{'FROM':num(-210),'TO':num(210)})
b(star,'a3','control_repeat_until',None,'a2',{'CONDITION':[2,'or'],'SUBSTACK':[2,'a4']})
b(star,'or','operator_or',None,'a3',{'OPERAND1':[2,'touch'],'OPERAND2':[2,'low']})
b(star,'touch','sensing_touchingobject',None,'or',{'TOUCHINGOBJECTMENU':[1,'touchmenu']})
b(star,'touchmenu','sensing_touchingobjectmenu',None,'touch',fields={'TOUCHINGOBJECTMENU':['Pemain',None]});star['blocks']['touchmenu']['shadow']=True
b(star,'low','operator_lt',None,'or',{'OPERAND1':[3,'y',[4,'0']],'OPERAND2':num(-170)})
b(star,'y','motion_yposition',None,'low')
b(star,'a4','motion_changeyby','a5','a3',{'DY':num(-5)})
b(star,'a5','control_wait',None,'a4',{'DURATION':num(.03)})
star['blocks']['a3']['next']='a6'
b(star,'a6','control_if',None,'a3',{'CONDITION':[2,'hit'],'SUBSTACK':[2,'a7']})
b(star,'hit','sensing_touchingobject',None,'a6',{'TOUCHINGOBJECTMENU':[1,'hitmenu']})
b(star,'hitmenu','sensing_touchingobjectmenu',None,'hit',fields={'TOUCHINGOBJECTMENU':['Pemain',None]});star['blocks']['hitmenu']['shadow']=True
b(star,'a7','data_changevariableby',None,'a6',{'VALUE':num(1)},{'VARIABLE':['Skor','score']})
project={'targets':[stage,player,star],'monitors':[{'id':id,'mode':'default','opcode':'data_variable','params':{'VARIABLE':name},'spriteName':None,'value':v,'width':0,'height':0,'x':8,'y':90+i*28,'visible':True,'sliderMin':0,'sliderMax':100,'isDiscrete':True} for i,(id,name,v) in enumerate([('score','Skor',0),('time','Waktu',30)])],'extensions':[],'meta':{'semver':'3.0.0','vm':'11.3.0','agent':'r2studio.dev sample'}}
sb=out/'Tangkap-Bintang.sb3'
with zipfile.ZipFile(sb,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('project.json',json.dumps(project));
    for name,data in assets.items():z.writestr(name,data)
readme='''TANGKAP BINTANG — PROJECT CONTOH
r2studio.dev | Rahmi Vina Shafira, M.Pd.

Ini bahan latihan contoh, bukan karya asli atau bukti penilaian Genta.
1. Buka https://scratch.mit.edu/projects/editor/
2. Pilih File > Load from your computer / Muat dari komputer.
3. Pilih Tangkap-Bintang.sb3, lalu klik bendera hijau.
4. Gerakkan keranjang dengan panah kiri dan kanan. Setiap tangkapan menambah 1 skor.
5. Permainan berhenti setelah 30 detik. Klik bendera hijau untuk mengulang.

Pertemuan 1: stage, sprite, bendera hijau, gerakan panah, posisi x/y.
Pertemuan 2: loop, kondisi sentuhan, variabel skor dan waktu.
Tantangan berikutnya: tambah suara dan batas gerak kiri/kanan.
'''
with zipfile.ZipFile(out/'genta-scratch.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.write(sb,sb.name);z.writestr('PANDUAN.txt',readme)
with zipfile.ZipFile(sb) as z:
    d=json.loads(z.read('project.json'))
    for t in d['targets']:
        for id,block in t['blocks'].items():
            for ref in [block['next'],block['parent']]:assert ref is None or ref in t['blocks']
print('Scratch archive checked:',sb)