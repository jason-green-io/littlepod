#!/bin/bash


# contentduration tweetsduration "title"

sleep 10

echo 3
tmux send -t minecraft:7 \
"/title greener_ca reset" c-M \
"/title greener_ca title {\"text\": \"3\"}" c-M

sleep 1

echo 2
tmux send -t minecraft:7 \
"/title greener_ca title {\"text\": \"2\"}" c-M

sleep 1

echo 1
tmux send -t minecraft:7 \
"/title greener_ca title {\"text\": \"1\"}" c-M

sleep 8

echo "$1 minute(s)"

tmux send -t minecraft:7 \
"/title greener_ca subtitle {\"text\": \"$3\", \"color\": \"gold\"}" c-M \
"/title greener_ca title {\"text\": \"Barlynaland\", \"color\": \"gold\"}" c-M

sleep $(( $1 * 60  ))
if [[ "$2" > 0 ]]; then
	echo tweets!

	tmux send -t minecraft:7 \
	"/title greener_ca title {\"text\": \"tweets\", \"color\": \"gold\"}" c-M

	sleep $(( $2 * 60 ))
fi
tmux send -t minecraft:7 \
"/title greener_ca title {\"text\": \"wrap it up\", \"color\": \"gold\"}" c-M

echo wrap it up

sleep 60

tmux send -t minecraft:7 \
"/title greener_ca times 20 160 20" c-M \
"/title greener_ca subtitle {\"text\": \"see you next time!\", \"color\": \"gold\"}" c-M \
"/title greener_ca title {\"text\": \"Barlynaland\", \"color\": \"gold\"}" c-M

sleep 12

tmux send -t minecraft:7 \
"/title greener_ca title {\"text\": \"done\}" c-M
