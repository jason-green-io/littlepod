function console () 
{
    while true; do 
        ncat localhost 7777
        sleep 1
    done
}

function fix () 
{ 
    while true; do
        echo "/execute in overworld run teleport $1 0 70 0";
        sleep 0.1;
    done | while true; do
        ncat localhost 7777;
        sleep 1;
    done
}


function who ()
{
	jq -Cc --arg x 1261 --arg y 70 --arg z -2732 --arg r 600 '{"name": input_filename, "Pos": .Pos} | select(.Pos[0] > ($x|tonumber) - ($r|tonumber) and .Pos[0] < ($x|tonumber) + ($r|tonumber) and .Pos[1] < ($y|tonumber) + ($r|tonumber) and .Pos[1] > ($y|tonumber) - ($r|tonumber) and .Pos[2] < ($z|tonumber) + ($r|tonumber) and .Pos[2] > ($z|tonumber) - ($r|tonumber))' $DATAFOLDER/seapigeon/ | less -R
}


function update ()
{
    MCVERSION=$1
    /usr/bin/envsubst '$WEBDATA $DATAFOLDER $GMAILPASSWORD $GMAILUSER $MCVERSION' < /minecraft/monitrc.envsubst > /minecraft/.monitrc
    monit reload
    sleep 2 
    monit restart commandblock
}

TERM=screen-256color
PATH=$HOME:$PATH
