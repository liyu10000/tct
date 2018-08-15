while true
do
    python3 api.py;
    status=$?
    if test $status -eq 0
    then
        echo "program exit normally"
    else
        echo "no files found"
        exit 1
    fi
done
