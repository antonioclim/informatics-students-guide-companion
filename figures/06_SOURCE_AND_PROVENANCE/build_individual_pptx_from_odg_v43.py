import uno, sys, time
from pathlib import Path
from com.sun.star.beans import PropertyValue
src_path=Path(sys.argv[1]); out_path=Path(sys.argv[2]); port=int(sys.argv[3])
def prop(n,v):
 p=PropertyValue(); p.Name=n; p.Value=v; return p
ctx0=uno.getComponentContext(); resolver=ctx0.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver',ctx0)
ctx=resolver.resolve(f'uno:socket,host=localhost,port={port};urp;StarOffice.ComponentContext'); smgr=ctx.ServiceManager
desktop=smgr.createInstanceWithContext('com.sun.star.frame.Desktop',ctx); dispatch=smgr.createInstanceWithContext('com.sun.star.frame.DispatchHelper',ctx)
src=desktop.loadComponentFromURL(uno.systemPathToFileUrl(str(src_path)),'_blank',0,(prop('Hidden',False),prop('ReadOnly',True)))
if src is None: raise RuntimeError('source load returned None')
sp=src.getDrawPages().getByIndex(0)
dst=desktop.loadComponentFromURL('private:factory/simpress','_blank',0,(prop('Hidden',False),))
dp=dst.getDrawPages().getByIndex(0)
while dp.getCount(): dp.remove(dp.getByIndex(0))
dp.Width=sp.Width; dp.Height=sp.Height; dp.BorderLeft=sp.BorderLeft; dp.BorderRight=sp.BorderRight; dp.BorderTop=sp.BorderTop; dp.BorderBottom=sp.BorderBottom
ctrl=src.getCurrentController(); coll=smgr.createInstanceWithContext('com.sun.star.drawing.ShapeCollection',ctx)
for i in range(sp.getCount()): coll.add(sp.getByIndex(i))
if not ctrl.select(coll): raise RuntimeError('select failed')
dispatch.executeDispatch(ctrl.Frame,'.uno:Copy','',0,()); time.sleep(.15)
dctrl=dst.getCurrentController(); dctrl.setCurrentPage(dp); dispatch.executeDispatch(dctrl.Frame,'.uno:Paste','',0,()); time.sleep(.25)
count=dp.getCount()
if count==0: raise RuntimeError('paste produced zero shapes')
dst.storeAsURL(uno.systemPathToFileUrl(str(out_path)),(prop('FilterName','Impress MS PowerPoint 2007 XML'),prop('Overwrite',True)))
dst.close(True); src.close(True)
print('OK',src_path.name,count)
