// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract HealthcarePlatform is ERC20 {
    // Health record structure
    struct HealthRecord {
        string dataHash;  // Hash of the health record (e.g., IPFS hash)
        uint256 timestamp;  // When the record was created
    }

    // Mapping from patient addresses to their health records
    mapping(address => HealthRecord[]) public healthRecords;

    // Mapping to control access to health records (patient -> (doctor -> permission))
    mapping(address => mapping(address => bool)) public accessPermissions;

    // Token constructor
    constructor(uint256 initialSupply) ERC20("HealthToken", "HLT") {
        _mint(msg.sender, initialSupply); // Mint initial tokens to the deployer
    }

    // Store a new health record
    function storeHealthRecord(string memory _dataHash) public {
        HealthRecord memory newRecord = HealthRecord(_dataHash, block.timestamp);
        healthRecords[msg.sender].push(newRecord);
    }

    // Grant access to a doctor or third party
    function grantAccess(address _doctor) public {
        accessPermissions[msg.sender][_doctor] = true;
    }

    // Revoke access from a doctor or third party
    function revokeAccess(address _doctor) public {
        accessPermissions[msg.sender][_doctor] = false;
    }

    // Retrieve health records (only accessible by the patient or someone with access)
    function getHealthRecords(address _patient) public view returns (HealthRecord[] memory) {
        require(msg.sender == _patient || accessPermissions[_patient][msg.sender], "Access Denied");
        return healthRecords[_patient];
    }

    // Reward users with tokens for healthy behaviors
    function rewardUser(address _user, uint256 _amount) public {
        _transfer(msg.sender, _user, _amount); // Transfer tokens from the sender to the user
    }
}


