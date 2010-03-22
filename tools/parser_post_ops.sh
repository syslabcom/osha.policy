cat $1 | sed -f tools/insert_header.sed | sed -e 's/xmlns:ns0/xmlns/' | sed -e 's/ns0://g' | xmllint --format -
