#!/bin/sh
cd C:\\Users\\yousu\\Documents\\GitHub\\Transaction-Data-Streamlit
git add --all
timestamp() {
  date +"at %H:%M:%S on %d/%m/%Y"
}
git commit -am "Regular auto-commit $(timestamp)"
git push origin master