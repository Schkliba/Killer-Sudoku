include "alldifferent.mzn";
include "int_set_channel.mzn";
% Standard Sudoku Init
int: Base;
int: N = Base * Base;
set of int: Domain = 1..N;
set of int: Brackets = 1..Base;
set of int: Tiles = 1..N*N;

%array[Domain, Domain] of Domain: start_setup;
array[Domain, Domain] of var Domain: board;

%constraint forall(i,j in Domain)(if start_setup[i,j] > 0 then board[i,j] = start_setup[i,j] else true endif );
constraint forall (i in Domain) (alldifferent( [ board[i,j] | j in Domain ]) ); 
constraint forall (j in Domain) (alldifferent( [ board[i,j] | i in Domain ]) ); 
constraint forall (yi, yj in Brackets)
            (alldifferent([ board[(yi-1)*Base + xi, (yj-1)*Base + xj]|xi, xj in Brackets ]));
