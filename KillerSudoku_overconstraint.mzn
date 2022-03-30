include "alldifferent.mzn";

% Standard Sudoku Init
int: Base;
int: N = Base * Base;
set of int: Domain = 1..N;
set of int: Brackets = 1..Base;
set of int: Tiles = 1..N*N;
int: digs = ceil(log(10.0,int2float(N))); % digits for output

array[Domain, Domain] of 0..N: start_setup;
array[Domain, Domain] of var Domain: board;

% Killer Sudoku Init

int: C; % number of cages
set of int: Cages = 1..C;
int: MaxSum = sum(i in Domain)(i*N); %maximal achievable sum
int: BracketSum = sum(i in Domain)(i); %max sum in row/bracket/column
array[Tiles] of Cages: tile2cage;

array[Tiles] of Domain: tiles_x = [((t-1) mod N)+1 |t in Tiles];
array[Tiles] of Domain: tiles_y = [floor((t - tiles_x[t])/N)+1|t in Tiles];
 
array[Cages] of 1..MaxSum: target_sum;
 
 
% Standard Sudoku constraints
constraint forall(i,j in Domain)(if start_setup[i,j] > 0 then board[i,j] = start_setup[i,j] else true endif );
constraint forall (i in Domain) (alldifferent( [ board[i,j] | j in Domain ]) ); 
constraint forall (j in Domain) (alldifferent( [ board[i,j] | i in Domain ]) ); 
constraint forall (yi, yj in Brackets)
            (alldifferent([ board[(yi-1)*Base + xi, (yj-1)*Base + xj]|xi, xj in Brackets ]));

% Killer Sudoku Constraints
constraint forall(c in Cages)(alldifferent([board[tiles_y[i], tiles_x[i]]| i in Tiles where tile2cage[i]=c]));
constraint forall(c in Cages)(sum(i in Tiles where tile2cage[i]=c)(board[tiles_y[i], tiles_x[i]]) = target_sum[c]);
constraint forall (i in Domain) (sum(j in Domain )(board[i,j]) = BracketSum); 
constraint forall (j in Domain) (sum(i in Domain )( board[i,j]) = BracketSum); 
constraint forall (yi, yj in Brackets)
            (sum(xi, xj in Brackets)(board[(yi-1)*Base + xi, (yj-1)*Base + xj]) = BracketSum);

solve :: int_search(board, first_fail, complete) satisfy;
output  [ show_int(digs,board[i,j]) ++ " " ++ 
         if j mod Base == 0 then " " else "" endif ++
         if j == N then
             if i != N then 
                if i mod Base == 0 then "\n\n" else "\n" endif 
         else "" endif else "" endif  
         | i,j in Domain ] ++ ["\n"];