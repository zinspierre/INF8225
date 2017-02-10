load 20news_w100
whos
n = 4;
m = size(newsgroups, 2);
o = ones(1, m);
i = 1:m;
j = newsgroups;
Y = sparse(i, j, o, m, n);

Theta = rand(4, 101)-0.5;
X = documents;
X = [X; ones(1,16242)];
taux_dapprentissage = 0.0005;   
possibleY = eye(n);


% calul de P(Y|X)
% haut = exp(sum((Y*Theta)' .*X));
% bas = sum(exp(Theta*X)); 
% % applique chaque classe (les 4 lg de theta) � toutes les instance X
% % matrice 4 *16242 avec r chaque instance (chaque col) la valeur obtenue
% % comme on veut la somme sur Y, on fait juset sum qui va sommer sur les col
% PYsC = haut./bas
% now si on veut une ligne pr chaque Y (pas que pr les vrai Y), on calc
% Theta*X => 4 lg avc ttes les instances (colonnes)
% ensuite pareil on divise par Z (sauf que l�, on divise par [Z;Z;Z;Z] car
% on a 4 lignes pr les 4 classes
% bas = sum(exp(Theta*X));
% res = exp(Theta*X) ./ [Z;Z;Z;Z]
% en gros ds le premier cas, on a 1 lg avc les classes correspondants � la
% v�rit�, et ds le second cas, on a 4 lignes pr chaque classes
% dc les valeur du premier cas, on les retrouve ds une des lignes du second
% cas


break

[XA, XV, XT, YA, YV, YT] = create_train_valid_test_splits(X, Y);


converged = false;

% calcul de la log vraisemblance
Z = sum(exp(Theta * XA)); %Teta * X pr faire le produit coeff x instance pr chaque classe
% on retrouve une matrice 4x16242 avc un score pr chaque classe pr chaque
% instance puis on somme sur les classes
numerateur = sum((YA * Theta)' .* XA); %Y*Theta => coeff corrspondant ) la bonne classe � chaque position du Y, on transpose pr avoir 101x16242 comme X
% sum pr avoir pr chaque instance une valeur 
sum(numerateur-log(Z));





yixi = YA' * XA';

% Z = repmat(sum(exp(Theta * X)),4,1);
% esperance = ((exp(Theta * X)./Z)' )' * X';
% gradient = yixi - esperance;
% min(min(a==gradient))
logV = -10e10;
while ~converged  
    oldLogV = logV

    Z = sum(exp(Theta * XA));
    left = sum((YA * Theta)' .* XA);
    logV = sum(left-log(Z))
    if abs(oldLogV-logV) < 0.1,
        converged = 1
    end
    % calcul de P(Y|X)
    up = exp(Theta*XA);
    PYsX = up ./ [Z;Z;Z;Z];
%     calcul du gradient
    right = PYsX * XA';
    gradient = -(yixi-right);

    %     update theta
    Theta = Theta - taux_dapprentissage * gradient;
    
end

% calcul de P(Y|X)
up = exp(Theta*XV); %numerateur
% Z = denominateur

Z = sum(exp(Theta * XV));
PYsX = up ./ [Z;Z;Z;Z];

myRes = max(PYsX);
realRes = sum(YV' .* PYsX);
sum(myRes==realRes)/length(myRes)
