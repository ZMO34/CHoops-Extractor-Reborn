// Header+0x18 consumer predicates, not a complete flag mapping. Synthetic only.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.*;
import java.util.*;
public class NativeMotionStateTrace extends GhidraScript {
 private boolean donor;
 private void word(EmulatorHelper e,long a,long v){e.writeMemoryValue(toAddr(a),4,v);}
 private void init(EmulatorHelper e){for(int i=0;i<32;i++)e.writeRegister("r"+i,0);e.writeRegister("r2",donor?0x40f2a98L:0xa54ac8L);e.writeRegister("xer_so",0);}
 private String gate(long bits,boolean absent) throws Exception {
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try{
   long actor=0x40002000L,anim=0x40003000L,slot=0x40004000L,header=0x40005000L;
   e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);word(e,actor+0x18,anim);word(e,anim+(donor?0x38:0x70),slot);word(e,slot,absent?0:header);word(e,header+24,bits);init(e);e.writeRegister("r31",actor);e.writeRegister(e.getPCRegister(),donor?0x471c3cL:0x3095f8L);
   boolean done=false,flagged=false;
   for(int step=0;step<64;step++){
    long pc=e.getExecutionAddress().getOffset();if(pc==(donor?0x471cf0L:0x3096d0L)){done=true;flagged=true;break;}if(pc==(donor?0x471c70L:0x30962cL)){done=true;break;}
    if(!e.step(monitor))throw new Exception("Flag predicate failure: "+e.getLastError());
   }
   if(!done||flagged!=(!absent&&(bits&0x3f0)!=0))throw new Exception("Native state predicate mismatch");
   return "{\"kind\":\"mask-0x3f0\",\"word\":"+bits+",\"absent\":"+absent+",\"flagged\":"+flagged+",\"passed\":true}";
  }finally{e.dispose();}
 }
 private String clear(long[] words) throws Exception {
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try{
   e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);long first=words.length==0?0:0x40002000L;
   if(donor)word(e,0x4ac3d00L,first);else{word(e,0xa5435cL,0x4000a000L);word(e,0x4000a000L,first);}
   List<byte[]> expected=new ArrayList<>();
   for(int i=0;i<words.length;i++){
    long actor=0x40002000L+i*0x100,data=0x40004000L+i*0x400,anim=0x40007000L+i*0x200,slot=0x40008000L+i*0x100,header=0x40009000L+i*0x100;
    word(e,actor+0x14,data);word(e,actor+0x18,anim);word(e,actor+0x5c,i+1<words.length?actor+0x100:0);word(e,anim+(donor?0x38:0x70),slot);word(e,slot,header);word(e,header+24,words[i]);
    byte[] sent=new byte[0x300];Arrays.fill(sent,(byte)0x5a);e.writeMemory(toAddr(data),sent);byte[] wanted=sent.clone();if((words[i]&0x40000000L)==0)Arrays.fill(wanted,donor?0x2b4:0x1e4,donor?0x2bc:0x1ec,(byte)0);expected.add(wanted);
   }
   init(e);e.writeRegister("LR",0x4000f000L);e.writeRegister(e.getPCRegister(),donor?0x38cc90L:0x23b794L);boolean done=false;
   for(int step=0;step<256;step++){
    if(e.getExecutionAddress().getOffset()==0x4000f000L){done=true;break;}
    if(!e.step(monitor))throw new Exception("Flag clear traversal failed: "+e.getLastError());
   }
   if(!done)throw new Exception("Flag clear bound exceeded");
   for(int i=0;i<words.length;i++)if(!Arrays.equals(expected.get(i),e.readMemory(toAddr(0x40004000L+i*0x400),0x300)))throw new Exception("Native context pair/untouched bytes mismatch");
   return "{\"kind\":\"bit30-context-pair\",\"actors\":"+words.length+",\"passed\":true}";
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  String[] a=getScriptArgs();if(a.length!=2)throw new Exception("Supply profile and NEW output JSON");donor=a[0].equals("nba-2k11");if(!donor&&!a[0].equals("college-hoops-2k8"))throw new Exception("Bad profile");Path out=Paths.get(a[1]);if(Files.exists(out))throw new Exception("Existing output refused");
  if(getInt(toAddr(donor?0x38ccb4:0x23b7b4))!=0x54000042||getInt(toAddr(donor?0x471c54:0x30960c))!=0x80040018)throw new Exception("Unsupported native state revision");
  List<String> rows=new ArrayList<>();for(long bits:new long[]{0,1,8,0x10,0x20,0x40,0x80,0x100,0x200,0x400,0x3e0,0x3f0,0x40000000L,0x800003f0L})rows.add(gate(bits,false));rows.add(gate(0,true));
  for(long bits:new long[]{0,0x40000000L,0x80000010L,0xffffffffL})rows.add(clear(new long[]{bits}));rows.add(clear(new long[]{0,0x40000010L}));rows.add(clear(new long[]{}));
  Files.writeString(out,"[\n"+String.join(",\n",rows)+"\n]",StandardOpenOption.CREATE_NEW);println("Native motion state "+a[0]+": "+rows.size()+" passed");
 }
}
