#! /usr/bin/perl

use strict;

# MD5 used to hash the URL parameters which then gets signed (so LearnUpon can
# verify the request)
use Digest::MD5 qw(md5_hex);

##### CONFIGURATION
# Some config options from your SQSSO settings panel in LearnUpon.
# These must match exactly!
# a) Your secret key, "{secret_key}"
my( $key ) = "eddb863434005f104e7b0c5d96";
# b) The message format, "Signed Token Format"
my( $message ) = "USER=##EMAIL##&TS=##TIME##&KEY=" . $key;
# c) The "SQSSO Entry point"
my( $urlSSO ) = "https://mysinglesignontest.learnupon.com/sqsso";
# d) The URL parameter names as setup in LU SQSOO
#    For example 'Email' is configured under (login_param} in LU SQSSO settings
#    The ##EMAIL## is just for PERL substitution that occurs later.
#    All the key names (Email=,Time=,SSOToken=, etc.) must match what is configured in LU.
$urlSSO .= "?Email=##EMAIL##&Time=##TIME##&SSOToken=##TOKEN##&FName=##FNAME##&LName=##LNAME##";

# This sample script has a hard-coded user database. It's a hash whose key
# is the username, and whose value is an array with Password,FirstName,LastName.
# It could also have Custom Data fields (as per LU SQSSO docs).
my( %users ) = (
	'joesoap1', [ 'mypassword', "Joe", "Soap", 'joesoap@does.not.exist.learnupon.com' ]
);


##### SCRIPT

# First, parse the request params provided (GET or POST) in to a hash
our( %params );
&setParams();

# Print standard HTTP/HTML header
print "Content-type: text/html\n\n";
print << "EOP";
<html>
	<head>
		<style type="text/css">
		</style>
	</head>
	<body>
EOP


# If username/password is provided, process SSO. Otherwise, just present login form.
if( $params{'u'} ne "" && $params{'p'} ne "" ) {
	# Based on the username provided, get the user from the hard-coded user store above.
	# Obviuosly, in a production environment, you'd check this against a database,
	# rather than a hard-coded user store!
	my( @user ) = @{ $users{ $params{'u'} } };
	if( $#user == 3 ) { #sanity check on user store array length

		# Check password matches
		if( $user[0] eq $params{'p'} ) {

			# Greeting to display
			print "<h1>Hello " . $user[1] . "</h1>";

			# Get current timestamp. This is important, because the same
			# timestamp will be used twice (and must be the same both times).
			# Once in the message/payload to be signed, and once as a SQSSO param
			my( $time ) = time;

			# Using the above configured message/payload, substitute "##" values
			# with real values from our hard-coded data store.
			$message =~ s/##EMAIL##/$user[3]/g;
			$message =~ s/##TIME##/$time/g;
			# Now that we have the message, generate an MD5 hash of it.
			# This hash will be compare on LearnUpon's side to ensure the
			# secret key, and core user parameters are valid.
			my( $token ) = md5_hex( $message );

			# Build up the URL to present to the user (for them to click to
			# login). This includes parameters that are used in the token above,
			# and includes additional parameters that don't form part of that token.
			# Ideally you would configure LearnUpon SQSSO "Signed Token Format"
			# field to include all parameters (so they can't be altered).
			$urlSSO =~ s/##EMAIL##/$user[3]/g;
			$urlSSO =~ s/##TIME##/$time/g;
			$urlSSO =~ s/##TOKEN##/$token/g;
			$urlSSO =~ s/##DEPARTMENT##/$user[4]/g;
			$urlSSO =~ s/##ICE##/$user[5]/g;
			$urlSSO =~ s/##FNAME##/$user[1]/g;
			$urlSSO =~ s/##LNAME##/$user[2]/g;

			# Present the sign in URL to the user. (Could also be just redirected
			# automatically there.)
			print "<p>URL: $urlSSO</p>";
			print "<button onclick=\"window.location='$urlSSO';\">Sign in to your eLearning Portal</button>";
		}
		else {
			# Some error message to show when the password isn't correct
			# You normally wouldn't say the username was correct, but password wasn't!
			print "<h1>:( Sad Face</h1>";
			print "<p>Could not log you in, as your password is incorrect.</p>";
		}
	}
	else {
		# Error message to show when the user couldn't be found.
		print "<h1>:( Sad Face " . $#user . "</h1>";
		print "<p>Could not log you in, as your username is not valid.</p>";
	}
}
else {
	# As no username/password params have been provided, display a (basic!)
	# login form
	print "<h1>Please Login</h1>";
	print '<form method="post">';
		print '<label for="idU">Username:</label><input id="idU" name="u" type="text" /><br />';
		print '<label for="idP">Password:</label><input id="idP" name="p" type="text" /><br />';
		print '<input value="Login" type="submit" />';
	print '</form>';
}

	print << "EOP";
	</body>
</html>
EOP

exit( 0 );

# Simple routine to parse GET/POST request params
sub setParams {
	my( @pairs );
	if( $ENV{'REQUEST_METHOD'} && $ENV{'QUERY_STRING'} && $ENV{'REQUEST_METHOD'} eq 'GET' ) { @pairs = split(/&/, $ENV{'QUERY_STRING'}); }
	elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
		my( $buffer );
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
		@pairs = split(/&/, $buffer);
	}
	my( $pair );
	foreach $pair (@pairs) {
		my($name, $value) = split(/=/, $pair);
		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$value =~ s/ *$//;
		$params{$name} = $value;
	}
}
