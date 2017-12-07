import difflib
from nbt.nbt import NBTFile, TAG_Long, TAG_Int, TAG_String, TAG_List, TAG_Compound
import pprint

nbtdataNew = NBTFile("6060debe-836f-4a45-95ab-4311a53972f7.new.dat")
nbtdataOld = NBTFile("6060debe-836f-4a45-95ab-4311a53972f7.old.dat")

pp = pprint.PrettyPrinter(depth=1, indent=4, width=10)


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


oldObj = unpack_nbt(nbtdataOld)["Inventory"]
newObj = unpack_nbt(nbtdataNew)["Inventory"]

def makeLine( item ):


    return "{0} s{1} c{2}".format(item.get("id").replace("minecraft:", ""), item.get("Slot"), item.get("Count"))


oldLines = [makeLine(a) for a in oldObj]
newLines = [makeLine(a) for a in newObj]

old = pp.pformat(oldObj).split()
new = pp.pformat(newObj).split()



differ = difflib.HtmlDiff()

print(differ.make_file(sorted(oldLines), sorted(newLines)))
