echo $(date) "Sending save-all to server"

{
echo "/save-off"
sleep 2
echo "/save-all flush"
sleep 10
} | ncat localhost 7777

echo $(date) "Syncing world to backup"

rsync --rsh "ssh -i $RSYNCKEY" -av --inplace --delete $DATAFOLDER/mc/world $RSYNCDEST:$SERVERNAME
restic backup $DATAFOLDER/mc/world
sleep 10
{
echo "/save-on"
sleep 1
} | ncat localhost 7777

echo $(date) "sync done"
