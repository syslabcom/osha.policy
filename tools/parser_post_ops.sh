cat $1 | sed -e 's/xmlns:ns0/xmlns/' | sed -e 's/ns0://g' | xmllint --format -
