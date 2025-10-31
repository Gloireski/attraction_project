export interface UserSession {
  id: number;
  session_key: string;
  profile_type: string;
  country: string;
  capital: string;
//   isLoading: string;
};

export interface createSessionResponse {
    userProfile: UserSession
    isLoading: string
}