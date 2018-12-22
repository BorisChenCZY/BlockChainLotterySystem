# BlockChainVoteSystem
## Motivation
In our daily life, we have many votes or questionnaire to finish. Some of them are anonymous, and some are not, as the vote claim. But we can only trust the anonymousness by trusting the host of that vote. If they actually abused the information in your vote, you just have no idea. Sometimes, the people who invoke a vote is different from those who collect the vote. So the vote collectors may change the vote result so to meet their benefits. Now, we introduce a technique called Blockchain Vote System to prevent those situations. Based on blockchain, people can not modify the vote result and the procedure is totally anonymous. And with our blind signature module, vote invoker can control the permission to people who can involve this vote but have no idea who is voting which one the whole procedure.

## Features and Requirements
### Web Server
- Vote
- User management
- Admin
### Block Chain
- Chain Struture
- P2P Network
### Blind Signature
For achieve a totally anonymous voting, we employ a technique named blind signature. The flow is following:
1. The first thing to be clear is that the system must have a centralized verification agency to verify that whether the voter has the right to vote. We call the agency C.
2. Voter A prepares a pair of public and private keys, with private key is s and public key is p.
3. A turns the public key p into p' through a blinding function and sends p' to the central authority C.
4. C checks A's voting eligibility, then signs p' with its private key, gets s', and returns it to A.
5. After A gets s', it can get s through the anti-blind function.
6. It can be proved that s is the signature of the public key p.
7. Now A can vote anonymously with the public keys p and s. Anyone can test that p is a voter who has been verified by the Central Organization C.

## User Interface
#### For PC Users &  Mobile USers
 - [x] Homepage
 - [x] Login in Page
 - [x] Block Information Page
 - [x] Start Vote Page
 - [x] Vote List Page
 - [x] Voting Pages 
 
#### Creat a Vote Demo
 ![](https://github.com/BorisChenCZY/BlockChainVoteSystem/blob/master/demo/demo.gif)

