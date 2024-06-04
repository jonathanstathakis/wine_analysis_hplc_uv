#!/bin/zsh

# find files in pwd and a target path and compare them using diff

dir_1="$1"
dir_2="$2"
pattern="$3"
echo "in the script.."
echo "input: dir_1='$dir_1'"
echo "input: dir_2='$dir_2'"
echo "search pattern: '$pattern'"

file_1=$(find $dir_1 -name $pattern)
file_2=$(find $dir_2 -name $pattern)
echo ""
echo "file_1_found:'$file_1'\n\nfile_2_found:'$file_2'"
echo "\n#############################################\n"
echo "Diff Results:"
echo $(diff -s $file_1 $file_2)
