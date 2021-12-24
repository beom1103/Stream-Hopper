import React from 'react';
import { Navigate } from 'react-router-dom';
import { useRecoilValue } from 'recoil';

import { authAtom } from '../store/userStore'

const PrivateRoute = ({ children }) => {

  const auth = useRecoilValue(authAtom);
  

  if (!auth) {
    alert("로그인 후 이용해주세요.")
    return <Navigate to="/login" />;
  }

  return children;
};

export default PrivateRoute;