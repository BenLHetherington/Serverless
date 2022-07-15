import React, { useEffect, useState } from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import './App.css'; 
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';

import githubLogo from 'images/githubLogo.png'

function App() {
  const [userCount, setUserCount] = useState(false);
  const [BlockSize, setBlockSize] = useState(false);
  const [RID, setRID] = useState(false);
  const [MVAL, setMVAL] = useState(false);
  const [DISCAASPMat, setDISCAASPMat] = useState(false);
  const [DISCBSPMat, setDISCBSPMat] = useState(false);
  const [DISCLBPMat, setDISCLBPMat] = useState(false);
  const [DISCAASPMean, setDISCAASPMean] = useState(false);
  const [DISCBSPMean, setDISCBSPMean] = useState(false);
  const [DISCLBPMean, setDISCLBPMean] = useState(false);
  // var [PassiveTable, setPassiveTable] = useState(false);

  //Special handling to use localhost SAM API if running locally via npm start(make run)
  const apiUrl = (process.env.NODE_ENV !== 'development') ? 'https://' + process.env.REACT_APP_USER_API_DOMAIN + '/users' : process.env.REACT_APP_USER_API_URL_LOCAL_SAM


  // function GenerateTable() {
  //   // Gate to catch if all params not filled
  //   if (!(factors)) {
  //     return null;
  //   }
  //   if (TotalSalesGrowth < 0) {
  //     return (
  //       <Typography variant='h5'>No further analysis as there is no positive growth to apportion between active and passive components</Typography>
  //     );
  //   }

  //   PassiveTable = [];
  //   for (let i = 0; i < Object.keys(factors).length; i++) {
  //     PassiveTable[i]={
  //       "Factor": factors[i][1],
  //       "BeginningValue": parseFloat(factors[i][5]),
  //       "EndingValue": parseFloat(factors[i][6]),
  //       "TotalGrowth": parseFloat(factors[i][3]*100),
  //       "Elasticity": parseFloat(factors[i][2]),
  //       "Impact": parseFloat(factors[i][4])
  //     };
  //   };
  //   console.log('PassiveTable: ', PassiveTable);
  //   // return (PassiveTable);
  //   return (
  //     <div className="App">
  //       <Typography >The passive appreciation estimate presented here is based on the data for a diversified collection of all businesses, nationwide, for each retail sector, The passive appreciation proportion for individual businesses may differ depending on the demographic and economic conditions specific to their area of operation. </Typography>
  //       <br/>
  //       <table>
  //         <tr>
  //           <th>Factor Name</th>
  //           <th>Beginning Value</th>
  //           <th>Ending Value</th>
  //           <th>Total Growth</th>
  //           <th>Elasticity</th>
  //           <th>Impact</th>
  //         </tr>
  //         {PassiveTable.map((val, key) => {
  //           return (
  //             <tr key={key}>
  //               <td>{val.Factor}</td>
  //               <td>{val.BeginningValue.toFixed(3)}</td>
  //               <td>{val.EndingValue.toFixed(3)}</td>
  //               <td>{val.TotalGrowth.toFixed(2)} %</td>
  //               <td>{val.Elasticity.toFixed(5)}</td>
  //               <td>{val.Impact.toFixed(6)}</td>
  //             </tr>
  //           )
  //         })}
  //       </table>
  //       {/* <br/>
  //       <Typography variant='h5'>Total Influencer Economic Factor Impact: {parseFloat(InfluencerEconomicFactorImpact*100).toFixed(2)} %</Typography>
  //       <Typography variant='h5'>Passive Growth: {parseFloat(passiveGrowthVar*100).toFixed(2)} %</Typography>
  //       <br/> */}
  //     </div>
  //   );
  // }


  // Prevent continuous reloading calling API each time
  // This makes the call to the backend
  useEffect(() => {
    if (BlockSize && RID && MVAL){
      //Variables being sent
      fetch(apiUrl+"?BlockSize="+BlockSize+"&RID="+RID+"&MVAL="+MVAL)
      .then(response => response.json())
      //Response variables
      .then(response => {
        console.log(response)
        setUserCount(response['User count'])
        setDISCAASPMat(response['DISCAASPMat'])
        setDISCBSPMat(response['DISCBSPMat'])
        setDISCLBPMat(response['DISCLBPMat'])
        setDISCAASPMean(response['DISCAASPMean'])
        setDISCBSPMean(response['DISCBSPMean'])
        setDISCLBPMean(response['DISCLBPMean'])
        //Console logging for debugging
        console.log('Length of DISCAASPMat Array: ', Object.keys(DISCAASPMat).length)
        console.log('Length of DISCBSPMat Array: ', Object.keys(DISCBSPMat).length)
        console.log('Length of DISCLBPMat Array: ', Object.keys(DISCLBPMat).length)
      })
      .catch(err => {
        console.log(err);
      });
    }
  }, [BlockSize, RID, MVAL] );
  
  return (
    <div className="App">
      <header className="App-header">
      <br/>
        <Container className='header' maxWidth='md'>
          <Typography variant='h2'>
            DLOM Calculator
          </Typography>
          <Typography variant='h5'>
          Dr. Ashok Abbott
          </Typography>
          <br/>
          <Typography variant='h5'>
          User Date: 
          </Typography>
          <form>
            <input type="month" id="start" name="start"
              min="1995-01" max="2021-12" onChange={RID => setRID(RID.target.value)} ></input>
          </form>
          <Typography variant='h5'>
          MVAL: 
          </Typography>
          <input type="number" 
            onChange={MVAL => setMVAL(MVAL.target.value)} ></input>
          <Typography variant='h5'>
          Block Size: 
          </Typography>
          <Typography>
          As a percentage between 0 and 100
          </Typography>
          <input type="number" min={0} max={100}
            onChange={BlockSize => setBlockSize(BlockSize.target.value)} ></input>
          <br/>
          <br/>
          <Typography>
          This demo shows PLACEHOLDER
          </Typography>
          <br/>
          <Typography variant='h6'>DISCAASPMean is {DISCAASPMean}</Typography>
          <Typography variant='h6'>DISCBSPMean is {DISCBSPMean}</Typography>
          <Typography variant='h6'>DISCLBPMean is {DISCLBPMean}</Typography>
          <br/>
          {/* {GenerateTable()} */}
          {/* {PrintTable()} */}
          {/* {pasiveGrowthPrintout()} */}
          {/* {FactorGrowthCheck()} */}
          <br/>
          <Typography className='visitorCounter'>Please contact "ashok.abbott@bizvalinc.com" with any questions/comments/suggestions</Typography>
          <Typography className='visitorCounter'>Visitor Count: {userCount}</Typography>
        </Container>
      </header>
    </div>
  );
}

export default App;
