use strict;
use warnings;

my %conv;

my $maps = "/home/larsmyg/Downloads/mappings-upc-2007/mapping-20-30/wn20-30"; 

foreach my $pos ("noun", "verb", "adj", "adv") {

    my $suf;
    if ($pos eq "noun") { $suf = "-n" }
    elsif ($pos eq "verb") { $suf = "-v" }
    elsif ($pos eq "adj") { $suf = "-a" }
    elsif ($pos eq "adv") { $suf = "-b" }

    open (F, "$maps.$pos");
    while (<F>) {
	my ($k, $v) = split(/ /);
	$k = $k . $suf;
	$v = $v . $suf;
	$conv{$k}=$v;
    }

}

while (<STDIN>) {
    chomp;
    my ($en, $gr) = split(/\t/);
    $en =~ s/^ENG20\-//;
    $gr =~ s/^wngre:synset\-//;
    $gr =~ s/\-.*//;
    $gr =~ s/_//g;


    my $en_3 = $conv{$en};

    next unless ($en_3);
    
    print $en_3, "\t", $gr, "\n";

}
