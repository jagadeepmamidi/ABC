// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract HealthcarePlatform is ERC20, Ownable {
    struct HealthRecord {
        string ipfsHash;
        uint256 timestamp;
    }

    mapping(address => HealthRecord[]) private patientRecords;
    mapping(address => mapping(address => bool)) private accessPermissions;

    event HealthRecordStored(address indexed patient, string ipfsHash);
    event AccessGranted(address indexed patient, address indexed grantee);
    event AccessRevoked(address indexed patient, address indexed grantee);
    event UserRewarded(address indexed user, uint256 amount);

    constructor(uint256 initialSupply) ERC20("HealthToken", "HLT") {
        _mint(msg.sender, initialSupply);
    }

    function storeHealthRecord(string memory _ipfsHash) public {
        HealthRecord memory newRecord = HealthRecord(_ipfsHash, block.timestamp);
        patientRecords[msg.sender].push(newRecord);
        emit HealthRecordStored(msg.sender, _ipfsHash);
    }

    function getHealthRecords() public view returns (HealthRecord[] memory) {
        require(msg.sender == owner() || accessPermissions[msg.sender][msg.sender], "Unauthorized access");
        return patientRecords[msg.sender];
    }

    function grantAccess(address _grantee) public {
        accessPermissions[msg.sender][_grantee] = true;
        emit AccessGranted(msg.sender, _grantee);
    }

    function revokeAccess(address _grantee) public {
        accessPermissions[msg.sender][_grantee] = false;
        emit AccessRevoked(msg.sender, _grantee);
    }

    function rewardUser(address _user, uint256 _amount) public onlyOwner {
        require(balanceOf(address(this)) >= _amount, "Insufficient balance for reward");
        _transfer(address(this), _user, _amount);
        emit UserRewarded(_user, _amount);
    }
}