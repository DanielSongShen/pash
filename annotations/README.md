Here is a preliminary version of the annotation language:

```
  <option> ::= `-' <string>
  <category> ::= `stateless' | `pure' | ...
  <maybe-int> ::= ε | <int>
  <arg> ::= `args[' <int> `]'
  <args> ::= <arg>
           | `args[' <maybe-int> `:' <maybe-int> `]'
  <input> ::= `stdin' 
            |  <args>
  <inputs> ::= <input>
             | <input> `,' <inputs>
  <output> ::= `stdout' 
             |  <arg>
  <outputs> ::= <output>
              | <output> `,' <outputs>
  <option-pred> ::= <option>
                  | `value' <option> = <string>
                  | `not' <option-pred>
                  | <option-pred> `or' <option-pred>
                  | <option-pred> `and' <option-pred>
  <assignment> ::= `(' <category>, `[' <inputs> `]' `,' `[' <output> `]' `)'
  <predicate> ::= <option-pred> `=>' <assignment>
  <pred-list> ::= `|' <predicate> <pred-list>
                | `|' `otherwise' `=>' <assignment>
  <command> ::= <name> `\{' <pred-list> `\}'
  <command-list> ::= <command>
                   | <command> <command-list>
```

**TODOs**: 
* Update the annotation language based on the most recent insights
* Convert `json` to `yaml` to improve human readability of annotations
* Describe key annotations and the annotation DSL using examples
