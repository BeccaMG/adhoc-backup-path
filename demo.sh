# remotecmd="echo -n 'The hostname of this computer is ' && echo \$HOSTNAME"
# ssh "$1" $remotecmd
# echo $HOSTNAME


# microproject_path="$HOME/appServ/EJBLabs/Microproject/"
# echo $microproject_path

microproject_path="`realpath $1`"
old_IFS=$IFS
IFS=$'\n'
lines=($(cat `realpath $2`)) # array
IFS=$old_IFS

for ip in $(cat `realpath $2`)

do
    echo $ip;
    cmd="python $microproject_path/main_experiment.py > $ip";
    gnome-terminal -x sh -c "ssh $ip \"echo 'Hi from $ip' && $cmd\"; bash"
# ac_address="${lines[1]}"  # Administration Client IPaddress/hostname
# mbm_address="${lines[2]}" # Mailbox Manager IPaddress/hostname
# mbc_address="${lines[3]}" # MailBox Client IPaddress/hostname
done
dms_script_path="$microproject_path/DirectoryManager/run_server.sh"
ac_script_path="$microproject_path/DirectoryManager/run_client.sh"
mbm_script_path="$microproject_path/MailBoxManager/run_server.sh"
mbc_script_path="$microproject_path/MailBoxClient/run_client.sh"

dms_cmd="sh $dms_script_path $mbm_address"  # Run the Directory Manager with the MailBox Manager address
ac_cmd="sh $ac_script_path $dms_address"    # Run the Administration Client with the Directory Manager address
mbm_cmd="sh $mbm_script_path $dms_address"  # Run the MailBox Manager with the Directory Manager address
mbc_cmd="sh $mbc_script_path $mbm_address"  # Run the MailBox Client with the MailBox Manager address

cmd="python $microproject_path/main_experiment.py > $HOSTNAME"

# gnome-terminal -x sh -c "ssh $mbm_address \"echo 'Hi from $mbm_address' && $cmd\"; bash"
# gnome-terminal -x sh -c "ssh $dms_address \"echo 'Hi from $dms_address' && $cmd\"; bash"
# gnome-terminal -x sh -c "ssh $ac_address \"echo 'Hi from $ac_address' && $cmd\"; bash"
# gnome-terminal -x sh -c "ssh $mbc_address \"echo 'Hi from $mbc_address' && $cmd\"; bash"
