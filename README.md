# encryp.io

Secure communication

## Planas


- [x] Milestone 1: Paprastas CL python client ir server app. Client ir server komunikuoja per sockets. No encryption.
- [x] Milestone 2: X3DH key publishing prototype
- [ ] Milestone 3: Sending initial message


## Signal protocol (end to end encryption)

### The X3DH (extended triple Diffie-Hellman) Key Agreement Protocol

https://signal.org/docs/specifications/x3dh/

---

**Alice**: wants to send Bob some data safely and establish a shared symmetric key

**Bob**: wants to allow parties like Alice to establish a shared symmetric key with him to do that, even if Bob is offline.

**Server**: store encrypted messages from Alice and Bob and store public keys

---

5 public keys (and corresponding private keys) are involved:

IKA - Alice's identity key (long term)
EKA - Alice's ephemeral key (short term)
IKB - Bob's identity key (long term)
SPKB - Bob's signed prekey (short term)
OPKB - Bob's one-time prekey (short term)

Keys: Curve25519 (https://en.wikipedia.org/wiki/Curve25519)

Prekeys: Bob publishes them to the server prior to Alice beginning the protocol run

During each protocol run, Alice generates a new ephemeral key pair with public key EKA.

After a successful protocol run Alice and Bob will share a 32-byte secret key SK (idea - 256-bits symmetric AES key)

---

Flow:

**1. Bob publishes his identity key and prekeys to a server**

Publish to the server:

• IKB (only once)

• SPKB 

• Signature(IKB, Encode(SPKB))

• A set of prekeys (OPKB1, OPKB2, ...) (Upload whenever server thinks it's necessary)

Every time a connection is established with the server, user sends the following message to the server:

```json
{
    "UID" : "User ID",
    "IKB" : "Identity key",
    "SPKB" : "Signed prekey",
    "Signature" : "Signature(IKB, Encode(SPKB))",
    "Prekeys" : [
    	{ "OPKB1" : "One-time prekey" },
        { "OPKB2" : "One-time prekey" },
        { "..." : "..." },
        { "OPKB5" : "One-time prekey" }
    ]
}
```

Server database fields:

```
Person (string)
IK (string)
SPK (string)
SIG (string)
OPK1 (string)
OPK2 (string)
OPK3 (string)
OPK4 (string)
OPK5 (string)
````

Server checks if the identity key for this person is the same as the one provided in JSON message. Afterwards it determines if it needs to update the other values and correspondingly parses them from the message.

Server then gives user confirmation that everything went fine and gives following options by sending the following message to Bob:

```json
{
	"Response" : "Success"
	"Message" : "Send user's name with whom you'd like to communicate"
}
```

Bob then has to send a JSON message to the server

```json
{
	"UID" : "Alice"
}
```

In case of an error, server sends the following response:

```json
{
	"Response" : "Error"
	"Message" : "Bad message"
}
```

If error occurs in user verification part, close the connection. If error occcurs when trying to find the user, just ask for a user name again

**2. Alice fetches a prekey bundle from the server and uses it to send an initial message to Bob**

Alice has to perform X3DH key agreement with Bob.

After Alice requests the server to communicate with Bob, Server sends Alice prekey bundle:

```json
{
	"Response" : "Success"
	"Message" : ""
}
````

Todo

**3. Bob receives and processes Alice's initial message**

Todo

## Sockets and JSON

Message: fixed length header ()