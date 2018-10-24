#!/bin/bash
# Finds a first occurrence in the call stack for methods which appear only
# in Python 3 codepath.

set -ex

TEST_NAME="apache_beam.transforms.sideinputs_test.SideInputsTest.test_iterable_side_input"

TMP_DIR="/tmp"

PY2_EXECUTION_OUT="$TMP_DIR/py2_execution_stack"
PY3_EXECUTION_OUT="$TMP_DIR/py3_execution_stack"

PY2_EXECUTION_FILTERED="$TMP_DIR/py2_execution_stack_filtered"
PY3_EXECUTION_FILTERED="$TMP_DIR/py3_execution_stack_filtered"

PY2_EXECUTION_SHORTENED="$TMP_DIR/py2_execution_stack_shortened"
PY3_EXECUTION_SHORTENED="$TMP_DIR/py3_execution_stack_shortened"

PY3_ONLY_METHODS="$TMP_DIR/py3_only_methods"

PY3_FIRST_OCCURRENCE_INDEXED="$TMP_DIR/py3_first_occurrence_indexed"
PY3_FIRST_OCCURRENCE_SORTED="$TMP_DIR/py3_first_occurrence_sorted"

function mkenv()
{
  if [ -z "$1" ]
  then
    echo "Specify environment name!"
  else
    CUR_DIR=$(pwd) ; cd ~ ; rm -rf $TMP_DIR/$1; virtualenv $TMP_DIR/$1 ; . $TMP_DIR/$1/bin/activate ; cd $CUR_DIR
  fi
}

function mkpy3env()
{
  if [ -z "$1" ]
  then
    echo "Specify environment name!"
  else
    CUR_DIR=$(pwd) ; cd ~ ; rm -rf $TMP_DIR/$1; virtualenv -p python3 $TMP_DIR/$1 ; . $TMP_DIR/$1/bin/activate ; cd $CUR_DIR
  fi
}


mkenv py27env
git clean -fdx
python ./setup.py sdist
pip install ./dist/apache-beam-2.8.0.dev0.tar.gz[test]
python ./setup.py test -s $TEST_NAME &> $PY2_EXECUTION_OUT || true

export BEAM_EXPERIMENTAL_PY3=1
mkpy3env py3env
git clean -fdx

python ./setup.py sdist
pip install ./dist/apache-beam-2.8.0.dev0.tar.gz[test]
python ./setup.py test -s $TEST_NAME &> $PY3_EXECUTION_OUT || true

< $PY2_EXECUTION_OUT grep @@ > $PY2_EXECUTION_FILTERED
< $PY3_EXECUTION_OUT grep @@ > $PY3_EXECUTION_FILTERED

< $PY2_EXECUTION_FILTERED awk '{print $4}' | sort | uniq > $PY2_EXECUTION_SHORTENED
< $PY3_EXECUTION_FILTERED awk '{print $4}' | sort | uniq > $PY3_EXECUTION_SHORTENED

comm -13 <(sort $PY2_EXECUTION_SHORTENED) <(sort $PY3_EXECUTION_SHORTENED) > $PY3_ONLY_METHODS 

rm $PY3_FIRST_OCCURRENCE_INDEXED || true

set +x
while IFS='' read -r line || [[ -n "$line" ]]; do
  first_match=$(grep -n " call function $line " $PY3_EXECUTION_OUT | head -n 1 | cut -f1 -d":")
  echo $line $first_match >> $PY3_FIRST_OCCURRENCE_INDEXED
done < $PY3_ONLY_METHODS 

set -x
< $PY3_FIRST_OCCURRENCE_INDEXED sort -nk 2,2 > $PY3_FIRST_OCCURRENCE_SORTED

< $PY3_FIRST_OCCURRENCE_SORTED head -n 25


