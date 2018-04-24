
// groovy sqsso.groovy joesoap1 joesoap@does.not.exist.learnupon.com eddb863434005f104e7b0c5d96 mysinglesignontest.learnupon.com
String userName  = args[0];  //joesoap1
String email     = args[1];  //joesoap@does.not.exist.learnupon.com
String key       = args[2];  //eddb863434005f104e7b0c5d96
String domain    = args[3];  //mysinglesignontest.learnupon.com


long time = System.currentTimeMillis() / 1000L;

/* Important - while you might want to URLEncode email - don't */
String message = String.format("USER=%s&TS=%s&KEY=%s", email, time, key);

java.security.MessageDigest md = java.security.MessageDigest.getInstance("MD5");
md.update(message.getBytes());
byte[] digest = md.digest();
String token = javax.xml.bind.DatatypeConverter.printHexBinary(digest).toLowerCase();


String urlSSO = "https://${domain}/sqsso?Email=%s&TS=%s&SSOToken=%s";
urlSSO = String.format(urlSSO, URLEncoder.encode(email, "UTF-8"), time, token);

println urlSSO;
