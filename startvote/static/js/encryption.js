var sig;
var rsaPrivateKey;

function init(privateKey){
    rsaPrivateKey = new RSAKey();
    rsaPrivateKey.readPrivateKeyFromPEMString(privateKey);
    console.log("inited");
}

function sign(msg){
	sig = new KJUR.crypto.Signature({"alg": "SHA1withRSA"});
	sig.init(rsaPrivateKey);
	return sig.signString(msg);
}

function generate_pair(){
	rsaKeypair = KEYUTIL.generateKeypair("RSA", 512);
	return rsaKeypair;
}

function toPCK1(key){
	return KEYUTIL.getPEM(key, "PKCS1PRV");
}

function toPKCS8(key){
	return KEYUTIL.getPEM(key, "PKCS1PUB");
}