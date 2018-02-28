#!/bin/bash

# -------------- MAIN
main() {
	[ $# != 1 ] && usage && error
	conf="$1"
	[ ! -f "$conf" ] && error no such file: $conf
	set_vars $conf || error invalid config file
	tables=$(execute 'select `table` from urls')

	for migration in migrate/*.migration
	do
		migrate_query=$(for table in $tables
		do
			mapfile -t queries < <(cat $migration | sed -e "s/%%%TABLE%%%/$table/g")
			while read query
			do
				echo $query
			done <<< $queries
		done)
		execute "$migrate_query"
	done
}


# -------------- FUNCTIONS
usage() {
	cat <<EOF
Usage:
	$0 <configuration file>
EOF
}

error() {
	[ "$1" != "" ] && echo $@
	exit 1
}

set_vars() {
	engine=sqlite
	host=127.0.0.1
	port=3306
	local db=0
	local line
	while read line
	do
		(echo $line | tr -d '[:space:]' | grep -iP '^#' > /dev/null) && continue
		(echo $line | grep -iP '^\[database\]$' > /dev/null) && db=1 && continue
		(echo $line | grep -iP '^\[.*\]$' > /dev/null) && db=0 && continue
		[ $db -eq 0 -o "$line" == "" ] && continue
		(echo $line | grep -i 'engine' > /dev/null) && engine=$(echo $line | cut -d= -f2 | tr -d '[:space:]')
		(echo $line | grep -i 'host' > /dev/null) && host=$(echo $line | cut -d= -f2 | tr -d '[:space:]')
		(echo $line | grep -i 'port' > /dev/null) && port=$(echo $line | cut -d= -f2 | tr -d '[:space:]')
		(echo $line | grep -i 'name' > /dev/null) && name=$(echo $line | cut -d= -f2 | tr -d '[:space:]')
		(echo $line | grep -i 'username' > /dev/null) && user=$(echo $line | cut -d= -f2 | tr -d '[:space:]')
		(echo $line | grep -i 'password' > /dev/null) && pass=$(echo $line | cut -d= -f2 | tr -d '[:space:]')
	done < $1
	[ "$engine" == "sqlite" ] && [ "$name" == "" -o ! -f "$name" ] && return 1 && return 0
	[ "$user" == "" -o "$pass" == "" -o "$name" == "" ] && return 1
	return 0
}

execute() {
	local query=$@
	case $engine in
		sqlite)
			sqlite3 "$name" "$query"
			;;
		mysql)
			mysql -h$host -P$port -u$user -p$pass $name -e "$query" 2>/dev/null | tail -n +2
			;;
	esac
}

# -------------- ENTRY
main $@
