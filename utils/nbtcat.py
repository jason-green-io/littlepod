from nbt.nbt import NBTFile, TAG_Long, TAG_Int, TAG_String, TAG_List, TAG_Compound
import pprint
import sys
import glob



files = glob.glob(sys.argv[1])


# print(files)




'''
position = [ bla.value for bla in nbtdata["Pos"] ]
dimension = nbtdata["Dimension"].value
UUIDleast = nbtdata["UUIDLeast"].value
UUIDmost = nbtdata["UUIDMost"].value
'''

def unpack_nbt(tag):
    """
    Unpack an NBT tag into a native Python data structure.
    """
    
    if isinstance(tag, TAG_List):
        return [unpack_nbt(i) for i in tag.tags]
    elif isinstance(tag, TAG_Compound):
        return dict((i.name, unpack_nbt(i)) for i in tag.tags)
    else:
        return tag.value


for each in files:

    nbtData = NBTFile(each)

    pp = pprint.PrettyPrinter(depth=1, indent=4, width=10)




    Obj = unpack_nbt(nbtData)

    pp.pprint(Obj)
    #print([a["Players"] for a in Obj["data"]["Teams"] if a["Name"] == "mute"])




