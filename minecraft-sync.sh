echo $(date) "Sending save-all to server"

{
echo "/save-off"
sleep 2
echo "/save-all flush"
sleep 10
} | ncat localhost 7777

echo $(date) "Syncing world to backup"

rsync -av --inplace --delete /minecraft/host/mcdata/world /minecraft/host/otherdata/mcbackup
#echo "$(date) Creating snapshot"
# sudo zfs snapshot main/minecraft/world@$(date +%Y%m%d%H%M)

sleep 10
{
echo "/save-on"
sleep 1
} | ncat localhost 7777

echo $(date) "sync done"
