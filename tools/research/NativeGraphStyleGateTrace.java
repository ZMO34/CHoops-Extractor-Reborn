// NBA11 graph style gate only. Synthetic memory; no playback or game mutation.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.*;
import java.util.*;
public class NativeGraphStyleGateTrace extends GhidraScript {
 private void word(EmulatorHelper e,long at,long value){e.writeMemoryValue(toAddr(at),4,value);}
 private String trace(int selector,String mode) throws Exception {
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try{
   long node=0x40002000L,state=0x40003000L,row=0x40004000L,context=0x40005000L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x6000]);word(e,node+20,selector);
   int[] families={-1,0,0,1,1,1,2,2,2,3,3,3,4,4,5,6,7,8};
   int[] slots={-1,0,1,0,1,2,0,1,2,0,1,2,0,1,0,0,0,0};
   int family=selector<families.length?families[selector]:-1,selected=selector<slots.length?slots[selector]:-1;
   for(int f=0;f<9;f++){
    long entry=row+32*f;word(e,state+0x4c+f*4,mode.equals("missing-row")&&f==family?0:entry);
    for(int slot=0;slot<3;slot++){
     long target=node+0x100;
     if(f==family&&slot==selected)target=mode.equals("missing-slot")?0:mode.equals("mismatch")?node+0x100:node;
     word(e,entry+4+slot*4,target);
    }
   }
   for(int i=0;i<32;i++)e.writeRegister("r"+i,0);
   e.writeRegister("r26",state);e.writeRegister("r29",mode.equals("null-node")?0:node);e.writeRegister("r31",context);
   e.writeRegister("r6",mode.equals("bypass")?1<<13:0);e.writeRegister("xer_so",0);e.writeRegister(e.getPCRegister(),0x46c0d4L);
   boolean complete=false,accepted=false;
   for(int step=0;step<128;step++){
    long pc=e.getExecutionAddress().getOffset();
    if(pc==0x46c0f8L){complete=true;accepted=true;break;}
    if(pc==0x46c1c8L||pc==0x46c1ccL){complete=true;break;}
    if(!e.step(monitor))throw new Exception("Style gate failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   boolean expected=mode.equals("bypass")||mode.equals("null-node")||selector==0||(selector<=17&&mode.equals("match"));
   if(!complete||accepted!=expected)throw new Exception("Style gate result mismatch");
   return "{\"selector\":"+selector+",\"mode\":\""+mode+"\",\"accepted\":"+accepted+",\"passed\":true}";
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  String[] a=getScriptArgs();if(a.length!=1)throw new Exception("Supply NEW output JSON");Path out=Paths.get(a[0]);if(Files.exists(out))throw new Exception("Existing output refused");
  if(getInt(toAddr(0x46c0ec))!=0x80090014||getInt(toAddr(0x46c280))!=0x2b800011)throw new Exception("Unsupported native gate revision");
  List<String> rows=new ArrayList<>();
  for(int selector=1;selector<=17;selector++)for(String mode:new String[]{"match","mismatch","missing-row","missing-slot"})rows.add(trace(selector,mode));
  rows.add(trace(0,"missing-row"));rows.add(trace(18,"match"));rows.add(trace(18,"bypass"));rows.add(trace(18,"null-node"));
  Files.writeString(out,"[\n"+String.join(",\n",rows)+"\n]\n",StandardOpenOption.CREATE_NEW);println("Native graph style gate: "+rows.size()+" cases passed");
 }
}
