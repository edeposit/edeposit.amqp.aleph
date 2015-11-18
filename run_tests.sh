#! /usr/bin/env bash

export PYTHONPATH="src/edeposit/amqp:$PYTHONPATH"
export TEST_PATH="tests"

function show_help {
    echo -e "Usage: $0 [-h] [-a] [-i] [-u]"
    echo
    echo -e "\t-h"
    echo -e "\t\tShow this help."
    echo -e "\t-a"
    echo -e "\t\tRun all tests."
    echo -e "\t-i"
    echo -e "\t\tRun integration test (requires sudo)."
    echo -e "\t-u"
    echo -e "\t\tRun unittest."
    echo
    exit;
}

function run_all_tests {
    py.test $TEST_PATH;
    exit
}

function run_int_tests {
    py.test "$TEST_PATH/integration";
    exit
}

function run_unit_tests {
    py.test "$TEST_PATH/unit";
    exit
}

while getopts "haiu" optname; do
    case "$optname" in
        "a")
            run_all_tests;
        ;;
        "i")
            run_int_tests;
        ;;
        "u")
            run_unit_tests;
        ;;
        "h")
            show_help;
        ;;
        "?")
            echo "Unknown option $OPTARG"
        ;;
        ":")
            echo "No argument value for option $OPTARG"
        ;;
        *)
            # Should not occur
            echo "Unknown error while processing options"
        ;;
    esac
done

show_help;