"""Confirmed PS3 ROST tables and writable fields; no generic byte editor."""
TABLES={'players':(0x0271AC,5685,308),'arenas':(0x1D5C84,379,28),'teams':(0x1D85E0,443,704),'coaches':(0x23F78C,1373,44)}
STRING_FIELDS={'players':{'last_name':0x10,'first_name':0x14},'teams':{'short_name':0x30,'abbreviation':0x34,'school_name':0x38,'mascot_plural':0x3c,'mascot_name':0x40},'arenas':{'arena_code':4,'arena_name':0x18},'coaches':{'coach_name':0x14,'abbreviation':0x18}}
# ROST reference targets point inside a row, not to the row's start.
# Canonical biases are corroborated across the vanilla table and old schema.
REFERENCES={'arena_index':(0x44,'arenas',0x19),'rival1_index':(0x4c,'teams',0x31),'rival2_index':(0x50,'teams',0x31),'rival3_index':(0x54,'teams',0x31),'coach_index':(0x60,'coaches',0x15),'assistant1_index':(0x64,'coaches',0x15),'assistant2_index':(0x68,'coaches',0x15)}
EDITABLE={'players':('first_name','last_name','jersey_number','height_inches','position_code'),'teams':('asset_id',*REFERENCES,'roster_slots'),'arenas':(),'coaches':()}
POSITIONS={0:'PG',1:'SG',2:'SF',3:'PF',4:'C'}
