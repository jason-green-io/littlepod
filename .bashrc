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

function update ()
{
    MCVERSION=$1
    /usr/bin/envsubst '$GMAILPASSWORD $GMAILUSER $MCVERSION' < /minecraft/monitrc.envsubst > /minecraft/.monitrc
    monit reload
    sleep 2 
    monit restart commandblock
}

TERM=screen-256color
PATH=$HOME:$PATH
