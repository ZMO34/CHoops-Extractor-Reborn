// NBA11 animation graph native fixups and motion binding. Synthetic memory only.
// Args: NEW_OUTPUT_JSON. No asset or executable mutation.
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
public class NativeAnimGraphTrace extends GhidraScript {
 private void word(EmulatorHelper e,long at,long value){e.writeMemoryValue(toAddr(at),4,value);}
 private String trace(int count,boolean grouped) throws Exception {
  EmulatorHelper e=new EmulatorHelper(currentProgram);
  try{
   long base=0x40004000L,table=0x40008000L,header=0x40009000L,group=0x4000a000L,done=0x4000f000L;
   byte[] initial=new byte[0x2000];Arrays.fill(initial,(byte)0x5a);e.writeMemory(toAddr(base),initial);
   Map<Integer,Long> changes=new TreeMap<>();int next=128;
   int[] strides={36,24,4,8,12,4,16,16,16,16,16,16,16,16,16,16};
   int[] counts=new int[16];Arrays.fill(counts,1);counts[0]=count;int[] offsets=new int[16];
   for(int i=0;i<16;i++){
    offsets[i]=next;word(e,base+i*4,counts[i]);word(e,base+64+i*4,next-(64+i*4)+1);
    changes.put(64+i*4,base+next);next+=counts[i]*strides[i];
   }
   // Every native pointer class gets a valid non-null and/or null representative.
   for(int i=0;i<16;i++)for(int n=0;n<counts[i];n++){
    int row=offsets[i]+n*strides[i];int[] fields;
    if(i==0){word(e,base+row+16,grouped&&n==0?1:0);fields=new int[]{24,32};}
    else if(i==1)fields=new int[]{12,20};
    else if(i==2)fields=new int[]{};
    else if(i==3)fields=new int[]{4};
    else if(i<7)fields=new int[]{0};
    else fields=new int[]{4,8,12};
    for(int f:fields){int at=row+f;boolean nullPointer=(f==32||f==20||f==8);long target=base+0x1800;
     word(e,base+at,nullPointer?0:target-(base+at)+1);changes.put(at,nullPointer?0:target);
    }
   }
   for(int n=0;n<count;n++){
    long target=header+n*64;word(e,table+n*4,grouped&&n==0?group:target);
    int row=offsets[0]+n*36;
    if(grouped&&n==0){word(e,group+12,target);changes.put(row,group);}
    changes.put(row+4,target);
   }
   byte[] before=e.readMemory(toAddr(base),initial.length);byte[] expected=before.clone();
   for(Map.Entry<Integer,Long> change:changes.entrySet())ByteBuffer.wrap(expected).putInt(change.getKey(),change.getValue().intValue());
   e.writeMemory(toAddr(0x40000000L),new byte[0x2000]);
   for(int i=0;i<32;i++)e.writeRegister("r"+i,0);
   e.writeRegister("r1",0x40001000L);e.writeRegister("r2",0x40f2a98L);e.writeRegister("r3",base);e.writeRegister("r4",table);
   e.writeRegister("LR",done);e.writeRegister("xer_so",0);e.writeRegister(e.getPCRegister(),0x37fc60L);
   boolean complete=false;int steps=0;
   for(;steps<8192;steps++){
    long pc=e.getExecutionAddress().getOffset();if(pc==done){complete=true;break;}
    if(!e.step(monitor))throw new Exception("Graph instruction failure at "+Long.toHexString(pc)+": "+e.getLastError());
   }
   if(!complete)throw new Exception("Graph instruction bound exceeded");
   if(!Arrays.equals(expected,e.readMemory(toAddr(base),initial.length)))throw new Exception("Graph pointer binding or untouched bytes mismatch");
   return "{\"nodes\":"+count+",\"grouped_node\":"+grouped+",\"steps\":"+steps+",\"passed\":true}";
  }finally{e.dispose();}
 }
 public void run() throws Exception {
  String[] args=getScriptArgs();if(args.length!=1)throw new Exception("Supply NEW output path");
  Path out=Paths.get(args[0]);if(Files.exists(out))throw new Exception("Existing output refused");
  if(getInt(toAddr(0x37fcd0))!=0x2f800000||getInt(toAddr(0x37fd2c))!=0x3bde0024||getInt(toAddr(0x8339ac))!=0x80030000)
   throw new Exception("Unsupported native graph revision");
  List<String> rows=new ArrayList<>();rows.add(trace(0,false));rows.add(trace(1,false));rows.add(trace(2,true));
  Files.writeString(out,"[\n"+String.join(",\n",rows)+"\n]\n",StandardOpenOption.CREATE_NEW);
  println("Native animation graph fixups: "+rows.size()+" cases passed");
 }
}

