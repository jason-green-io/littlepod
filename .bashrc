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

TERM=screen-256color
export PATH=$HOME:$PATH
echo Read .bashrc
