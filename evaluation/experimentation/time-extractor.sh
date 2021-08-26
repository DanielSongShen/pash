EXTRACTOR="awk -F: '{ print ($1 * 60) + $2 }'"
cat "$PASH_TOP/../common-commands-time.out" | EXTRACTOR