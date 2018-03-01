# *Daadkvs* as a Distributed Key-Value Store

We implement a distributed key-value store called *Daadkvs* (**D**aadkvs **a**s **a** 
**D**istributed **K**ey-**V**alue **S**tore). *Daadkvs* implements an eventually consistency model.
Each entry in the store will be a pair of binary strings. The system will consist of clients and servers.
Servers will store the data and perform updates when asked by the clients. Clients will be able
to perform the following operations:

- **Put**:​ a new entry into the store.
- **Get**:​ the value associated with a key

In addition, we provide two session guarantees:

- *Read Your Writes*: if a client has written a value to a key, it will never read an older value.
- *Monotonic Reads*: if a client has read a value, it will never read an older value.

## Implementation


## Protocol


## Tests and Performance


## How to use our system


## Authors (listed in alphabetical order of last name)

- Jianwei Chen @JianweiCxyz (UT EID: UTCS id: )
- Zeyuan Hu @xxks-kkk (UT EID: zh4378 UTCS id: zeyuanhu)
- Wei Sun @sunwell1994 (UT EID: ; UTCS id: )