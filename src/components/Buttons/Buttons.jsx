import { useState,useEffect } from 'react'

import './Buttons.sass'


export default function Buttons({ dealInfo,allFiles,setDealData }) {

  const nextFile = () => {
    var currentIndex = allFiles.indexOf(dealInfo)
    if (currentIndex > -1 && allFiles.length > 1) {
      setDealData(allFiles[(currentIndex+1) % allFiles.length])
    } else if (currentIndex === -1) {
      setDealData(allFiles[0])
    }
  }

  return (
    <div className='button-container'>
      <button className='button' onClick={() => {
        window.pywebview.api.find_file()
      }}>Find File</button>
      <button className='button' onClick={nextFile}>Next</button>
    </div>
  )
}
