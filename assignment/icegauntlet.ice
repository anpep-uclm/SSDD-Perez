module IceGauntlet {
  exception Unauthorized {};
  exception RoomAlreadyExists {};
  exception RoomNotExists {};
  exception InvalidRoomFormat {};

  /**
   * Game interface (Client<->Server)
   */
  interface Game {
    /**
     * @brief Obtains the room data
     * @return The JSON string representing the room
     * @throws RoomNotExists 
     */
    string getRoom() throws RoomNotExists;
  };
  
  /**
   * Map management interface (Client<->Server)
   */
  interface MapManagement {
    /**
     * @brief Publishes a room
     * @description The client sends a room to the server and verifies the
     * token against the authentication server.
     * @param token Authentication token
     * @param roomData JSON string representing the room
     * @throws Unauthorized if the authentication token is not valid
     * @throws RoomAlreadyExists if a room with that name is already present on the server
     * @throws InvalidRoomFormat if the room data does not have the expected format
     */
    void publish(string token, string roomData) throws Unauthorized, RoomAlreadyExists, InvalidRoomFormat;
    
    /**
     * @brief Removes a room from the server
     * @param token Authentication token
     * @param roomName Name of the room to be removed
     * @throws Unauthorized if the authentication token is not valid
     * @throws RoomNotExists if no room with the specified name has been published
     */
    void remove(string token, string roomName) throws Unauthorized, RoomNotExists;
  };

  /**
   * Authentication interface (Client<->AuthServer)
   */
  interface Authentication {
    void changePassword(string user, string currentPassHash, string newPassHash) throws Unauthorized;
    string getNewToken(string user, string passwordHash) throws Unauthorized;
    bool isValid(string token);
  };
};
