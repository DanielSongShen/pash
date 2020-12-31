
### Meeting Agenda 12/14

* Started the OSX port; but hit on two types of problems — PaSh's runtime commands are not POSIX. We can fix this, but it will require resources outside . Until then, it might make sense to focus on our measurements on Linux machines. More updates next week.
* Started a simple CI server. The focus is to monitor correctness, not performance: It runs all our benchmarks with small inputs, and the smoosh suite.
* The experience of setting up PaSh on various machines is that it's insanely difficult due to its Python and OCaml dependencies. We need to solve this, because it's really affecting our ability to recruit students to work with the three of us on the project.
* We have two new benchmark sets: (i) modern aliases from GitHub (4,820,352 aliases -> 211,982 with pipes), which involve no expansion and are expected to be interactive (ii) NLP pipelines from the solutions from "unix for poets"
* K: Used the smoosh tests to solve a lot of surface level issues with PaSh. We started from ~20/174 passing and now we are ~90/174. The PaSh runtime (shell scripts) has been almost completely decoupled from the PaSh compiler (python scripts), allowing us to work independently on improving the correctness of PaSh and the performance and correctness of the compiler.
* K: Worked on issue #75, improving the hacky backend to a less hacky one that doesn't produce the script as a string but rather produces an AST. With this momentum, I should probably now focus on cleaning up the internal representation of PaSh, also fixing related issues (like #77) and assumptions that are not general enough.
* K: Regarding dependencies, we need to discuss how easy would it be to reimplement Python bindings for libdash.
* K: Does Michael need any help merging the expansion branch?
* K: After working through many smoosh tests I now have several questions and issues (that are not trivial to address) regarding the PaSh runtime. We can discuss as many of them as we can during the meeting.


**Issues with dependencies**

Two issues: [73](https://github.com/andromeda/pash/issues/73), [74](https://github.com/andromeda/pash/issues/74)

Problems with Python 3.8
* The fact that we can only run with a single python version is a huge impediment
* https://github.com/pypa/pip/issues/5367
* https://stackoverflow.com/questions/58758447/how-to-fix-module-platform-has-no-attribute-linux-distribution-when-instal

Problems with OCaml
* https://github.com/janestreet/install-ocaml — no repos for debian, requires downloading manually pre-built opam binary
* when trying to install OCaml with the opam binary, you hit bwrap — an external sandboxing dependency not part of OCaml.
* The related opam issue from 2018 (https://github.com/ocaml/opam/issues/3424) even has a couple of posts from Xavier Leory !
