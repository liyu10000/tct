while true
do
    python3 api.py;
    status=$?
    if test $status -eq 0
    then
        echo "finished one round."
    else
        echo "exit bash shell."
        exit 1
    fi
done
