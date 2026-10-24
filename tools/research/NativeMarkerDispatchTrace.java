// Exercise actual marker-ID indexing and OPD callback transfer, stopping at callbacks.
// Args: nba-2k11|college-hoops-2k8 NEW_OUTPUT_JSON. No game or callback runs.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.*;
import java.util.*;
public class NativeMarkerDispatchTrace extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs();
  if(args.length!=2)throw new Exception("Supply profile and NEW output path");
  boolean donor=args[0].equals("nba-2k11");
  if(!donor&&!args[0].equals("college-hoops-2k8"))throw new Exception("Unknown profile");
  Path output=Paths.get(args[1]);if(Files.exists(output))throw new Exception("Existing output refused");
  long base=donor?0x3e85474L:0x8ac024L,toc=donor?0x40f2a98L:0xa54ac8L;
  long start=donor?0x18330L:0x27168L,call=donor?0x18354L:0x2719cL;
  int count=donor?192:185;
  if(getInt(toAddr(call))!=0x4e800421||getInt(toAddr(donor?0x18344:0x27188))!=0x81690004)
   throw new Exception("Unsupported dispatch revision");
  List<String> rows=new ArrayList<>();
  for(int id=0;id<count;id++){
   long descriptor=Integer.toUnsignedLong(getInt(toAddr(base+id*8+4)));
   long entry=Integer.toUnsignedLong(getInt(toAddr(descriptor)));
   if(Integer.toUnsignedLong(getInt(toAddr(descriptor+4)))!=toc)throw new Exception("Unexpected callback TOC");
   EmulatorHelper e=new EmulatorHelper(currentProgram);
   try {
    long event=0x40002000L,header=0x40003000L,holder=0x40004000L,actor=0x40005000L;
    e.writeMemory(toAddr(0x40000000L),new byte[0x10000]);
    e.writeMemoryValue(toAddr(event),4,id);e.writeMemoryValue(toAddr(event+4),4,0x3fc00000);
    // Poison donor payload: this verifies transfer, not payload interpretation.
    e.writeMemoryValue(toAddr(event+8),4,0xdeadbeefL);e.writeMemoryValue(toAddr(holder),4,header);
    e.writeRegister("r1",0x40001000L);e.writeRegister("r2",toc);e.writeRegister("r11",event);
    if(donor){e.writeRegister("r27",base);e.writeRegister("r4",header);e.writeRegister("r5",actor);}
    else {e.writeRegister("r26",base);e.writeRegister("r22",actor);e.writeRegister("r9",event+4);e.writeRegister("r10",holder);}
    e.writeRegister(e.getPCRegister(),start);boolean done=false;
    for(int step=0;step<32;step++){
     long pc=e.getExecutionAddress().getOffset();
     if(pc==entry){
      if(e.readRegister("r3").longValue()!=(donor?event:id)||e.readRegister("r4").longValue()!=header
         ||e.readRegister(donor?"r5":"r6").longValue()!=actor||e.readRegister("r2").longValue()!=toc
         ||e.readRegister("LR").longValue()!=call+4)throw new Exception("Callback ABI mismatch");
      if(!donor&&e.readRegister("f1").longValue()!=Double.doubleToRawLongBits(1.5))throw new Exception("Marker time mismatch");
      rows.add("{\"id\":"+id+",\"flags\":"+getInt(toAddr(base+id*8))+",\"entry\":"+entry+",\"passed\":true}");done=true;break;
     }
     if(!e.step(monitor))throw new Exception("Instruction failure at "+Long.toHexString(pc)+": "+e.getLastError());
    }
    if(!done)throw new Exception("Dispatch instruction bound exceeded");
   }finally{e.dispose();}
  }
  Files.writeString(output,"[\n"+String.join(",\n",rows)+"\n]\n",StandardOpenOption.CREATE_NEW);
  println("Native marker dispatch: "+rows.size()+" cases passed");
 }
}
