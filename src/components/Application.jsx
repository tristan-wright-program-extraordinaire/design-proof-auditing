import { useState,useEffect,useRef } from 'react'

import DealInfo from './DealInfo/DealInfo'
import NasFolder from './NasFolder/NasFolder'

import nextIcon from '../assets/arrow-icon.png'
import orangeCircle from '../assets/loading_orange_circle.png'
import whiteHoop from '../assets/loading_white_hoop.png'
import blackHoop from '../assets/loading_black_hoop.png'
import indesignLogo from '../assets/indesign_icon.png'
import finderLogo from '../assets/finder_icon.png'
import zohoLogo from '../assets/zoho_icon.png'
import mailLogo from '../assets/mail_icon.png'

import './Application.sass'

const stages = ["Accept","Reject","Fix"]
const approvalStages = ["Normal","Rushed","ABD"]

export default function App () {
  const [allInvoices, setAllInvoices] = useState([])
  const [dealInfo, setDealData] = useState()
  const [importedFiles, setImportedFiles] = useState({})
  const [allFiles, setAllFiles] = useState({})
  const [attachments, setAttachments] = useState([])
  const [downloadFiles, setDownloadFiles] = useState([])
  const [downloadAttachments, setDownloadAttachments] = useState([])
  const [loading, setLoading] = useState(false)
  const [index,setIndex] = useState(-1)
  const [attachmentObject,setAttachmentObject] = useState({})
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [duplicateFiles, setDuplicateFiles] = useState([])
  const [fixableFiles, setFixableFiles] = useState([])
  const [findNasFolders, setFindNasFolders] = useState([])
  const [approved, setApproved] = useState([])
  const [rejected, setRejected] = useState([])
  const [rejectedEmails, setRejectedEmails] = useState([])
  const [errorDetails, setErrorDetails] = useState({})
  const [successDetails, setSuccessDetails] = useState({})
  const [missingFiles, setMissingFiles] = useState([])
  const [activeStage, setActiveStage] = useState("Accept")
  const [activeApprovalStage, setActiveApprovalStage] = useState("Normal")
  const [emailLoadingPercentage,setEmailLoadingPercentage] = useState({})

  const selectionRef = useRef(null)
  const drawerRef = useRef(null)
  const mainRef = useRef(null)

  useEffect(() => {
    window.addEventListener('pywebviewready', function () {
      if (!window.pywebview.state) {
        window.pywebview.state = {}
      }
      // Expose setImportedFiles in order to call it from Python
      window.pywebview.state.setImportedFiles = setImportedFiles
      window.pywebview.state.setLoading = setLoading
      window.pywebview.state.setDownloadAttachments = setDownloadAttachments
      window.pywebview.state.setDrawerOpen = setDrawerOpen
      window.pywebview.state.setDuplicateFiles = setDuplicateFiles
      window.pywebview.state.setFindNasFolders = setFindNasFolders
      window.pywebview.state.setFixableFiles = setFixableFiles
      window.pywebview.state.setApproved = setApproved
      window.pywebview.state.setRejected = setRejected
      window.pywebview.state.setRejectedEmails = setRejectedEmails
      window.pywebview.state.setMissingFiles = setMissingFiles
      window.pywebview.state.setErrorDetails = setErrorDetails
      window.pywebview.state.setSuccessDetails = setSuccessDetails
      window.pywebview.state.setEmailLoadingPercentage = setEmailLoadingPercentage
    })
  }, [])

  useEffect(() => {
    if (emailLoadingPercentage) {
      console.log("Email Loading Percentage")
      console.log(emailLoadingPercentage)
    }
  }, [emailLoadingPercentage])

  useEffect(() => {
    if (loading) {
      setLoading(false)
      setAllFiles(importedFiles)
      setAllInvoices(Object.keys(importedFiles))
      setIndex(-1)
      setAttachmentObject({})
    }
  }, [importedFiles])

  useEffect(() => {
    setAttachmentObject(prevObj => {
      var currentInvoice = allInvoices[index]
      var editedObj = {...prevObj}
      editedObj[currentInvoice] = attachments.concat(downloadAttachments)
      return editedObj
    })
  }, [downloadAttachments])

  useEffect(() => {
    if (allInvoices.length > 0) {
      nextFile()
    } else {
      setDealData(null)
    }
  }, [allFiles])

  useEffect(() => {
    console.log(allInvoices)
    console.log(index)
    console.log(allFiles)
    if (allInvoices.length > 0) {
      var nextDealInfo = allFiles[allInvoices[index]]
      setDealData(nextDealInfo)
      if (index > -1) {
        setActiveStage(allFiles[allInvoices[index]].status)
        setActiveApprovalStage(allFiles[allInvoices[index]].approval_type)
      } else {
        setActiveStage(allFiles[allInvoices[0]].status)
        setActiveApprovalStage(allFiles[allInvoices[0]].approval_type)
      }
    }
  }, [index])

  useEffect(() => {
    if (allInvoices.length > 0) {
      window.pywebview.api.download_files(downloadFiles)
    }
  }, [downloadFiles])

  useEffect(() => {
    if (drawerOpen) {
      mainRef.current.style.display = "flex"
    } else {
      mainRef.current.style.display = "block"
    }
  }, [drawerOpen])

  useEffect(() => {
    if (rejectedEmails) {
      setRejected(alreadyRejected => [...alreadyRejected,...rejectedEmails])
    }
  },[rejectedEmails])

  useEffect(() => {
    if (Object.keys(errorDetails).length > 0) {
      
    }
  },[errorDetails])

  function downloadMissingAttachments(nextDealInfo) {
    var fileLocations = []
    var tempFiles = []
    nextDealInfo.attachments.forEach(attachment => {
      if("geo_file" in attachment) {
        fileLocations.push(attachment.geo_file)
      } else {
        tempFiles.push({
          "deal_id": nextDealInfo.deal_id,
          "attachment_id": attachment.id,
          "attachment_name": attachment.name
        })
      }
    })
    setDownloadFiles(tempFiles)
    setAttachments(fileLocations)
  }

  const nextFile = () => {
    hideAttachments()
    if (index > -1 && allInvoices.length > 1) {
      var tempIndex = (index+1) % allInvoices.length
    } else if (allInvoices.length === 1) {
      var tempIndex = 0
    } else if (index === -1) {
      var tempIndex = 0
    }
    setIndex(tempIndex)
  }

  const previousFile = () => {
    hideAttachments()
    if (index > 0 && allInvoices.length > 1) {
      setIndex((index-1) % allInvoices.length)
    } else if (allInvoices.length === 1) {
      setIndex(0)
    } else if (index === 0) {
      setIndex(allInvoices.length - 1)
    } else if (index === -1) {
      setIndex(0)
    }
  }

  const selectStageOption = (e) => {
    if (e.target.tagName === "SPAN") {
      var target = e.target.parentElement
    } else {
      var target = e.target
    }
    setActiveStage(target.getAttribute("name"))
  }

  const selectApprovalStageOption = (e) => {
    if (e.target.tagName === "SPAN") {
      var target = e.target.parentElement
    } else {
      var target = e.target
    }
    setActiveApprovalStage(target.getAttribute("name"))
  }

  const submitProof = () => {
    setAllFiles(files => {
      var thisFile = {...dealInfo,"status":activeStage.toString(),"approval_type":activeApprovalStage.toString()}
      var updatedFiles = {...files}
      updatedFiles[thisFile.invoice] = thisFile
      return updatedFiles
    })
  }

  const sendEmails = () => {
    window.pywebview.api.send_emails()
  }

  const showOptions = () => {
    hideAttachments()
    selectionRef.current.classList.remove('hidden')
  }

  const clearFiles = () => {
    window.pywebview.api.clear_files()
    selectionRef.current.classList.add('hidden')
    setAllFiles({})
    setAllInvoices([])
  }
  
  const submitFiles = () => {
    window.pywebview.api.submit_files(allFiles)
    selectionRef.current.classList.add('hidden')
    setAllFiles({})
    setAllInvoices([])
  }

  const cancelFinished = () => {
    selectionRef.current.classList.add('hidden')
  }

  const showAttachments = () => {
    window.pywebview.api.open_drawer()
    if (!(allInvoices[index] in attachmentObject)) {
      downloadMissingAttachments(dealInfo)
    }
  }
  
  const hideAttachments = () => {
    window.pywebview.api.close_drawer()
  }

  const submitNas = () => {
    console.log("Submit NAS")
    console.log(findNasFolders)
    window.pywebview.api.submit_nas(findNasFolders)
  }
  
  const openZoho = (e) => {
    console.log("Open Zoho")
    window.pywebview.api.open_zoho(e.target.getAttribute('deal-id'))
  }

  const openPrintJobZoho = (e) => {
    console.log("Open Print Job Zoho")
    console.log(dealInfo)
    window.pywebview.api.open_print_job_zoho(e.target.getAttribute('print-job-id'))
  }

  const openInDesign = (e) => {
    console.log("Open InDesign")
    window.pywebview.api.open_indesign(e.target.getAttribute('deal-id'))
  }

  const openInDesignMissing = (e) => {
    console.log("Open InDesign Missing")
    window.pywebview.api.open_indesign_missing(e.target.getAttribute('indesign_path'))
  }

  const openFinderFix = (e) => {
    console.log("Open Finder")
    window.pywebview.api.open_finder_fixable(e.target.getAttribute('deal-id'))
  }

  const openFinderApprove = (e) => {
    console.log("Open Finder")
    window.pywebview.api.open_finder_approved(e.target.getAttribute('deal-id'))
  }

  const openFinderDupe = (e) => {
    console.log("Open Finder")
    window.pywebview.api.open_finder_duplicate(e.target.getAttribute('deal-id'),e.target.getAttribute('path'))
  }

  const openFinderMissing = (e) => {
    console.log("Open Finder")
    window.pywebview.api.open_finder_missing(e.target.getAttribute('path'))
  }
  
  const sendEmail = (e) => {
    console.log("Send Email")
    window.pywebview.api.send_email(e.target.getAttribute('deal-id'))
  }

  const fixed = () => {
    setFixableFiles([])
  }

  const approve = () => {
    setApproved([])
  }

  const reject = () => {
    setRejected([])
  }

  const duplicate = () => {
    setDuplicateFiles([])
  }

  const missing = () => {
    setMissingFiles([])
  }


  if (missingFiles.length > 0 && !loading) {
    return (
      <div className="nas_content">
        <span ref={selectionRef}/>
        <span ref={mainRef}/>
        <div className="title" style={{backgroundColor:"#701616"}}>
          <span>Missing Files</span>
          <button className="bookmarkBtn" onClick={missing}>
            <span className="IconContainer">
              <svg viewBox="2 0 12 15" height="2em" className="icon">
                <path
                  d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425z"
                ></path>
              </svg>
            </span>
            <p className="text">Submit</p>
          </button>
        </div>
        <div className="nasFolders">
          {missingFiles.map((deal) => (
              <div className="nasFolder" >
                <div className="name">{deal.invoice}</div>
                <button><img src={indesignLogo} alt="InDesign" indesign_path={deal.indesign_file} className="nasButton" onClick={openInDesignMissing} /></button>
                <button><img src={finderLogo} path={deal.path} alt="Finder" className="nasButton" onClick={openFinderMissing} /></button>
              </div>
            ))}
        </div>
      </div>
    )
  } else if (duplicateFiles.length > 0 && !loading) {
    return (
      <div className="nas_content">
        <span ref={selectionRef}/>
        <span ref={mainRef}/>
        <div className="title" style={{backgroundColor:"#701616"}}>
          <span>There Already Was A File There</span>
          <button className="bookmarkBtn" onClick={duplicate}>
            <span className="IconContainer">
              <svg viewBox="2 0 12 15" height="2em" className="icon">
                <path
                  d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425z"
                ></path>
              </svg>
            </span>
            <p className="text">Submit</p>
          </button>
        </div>
        <div className="nasFolders">
          {duplicateFiles.map((deal) => (
              <div className="nasFolder" >
                <div className="name">{deal.deal_name}</div>
                <button><img src={zohoLogo} alt="Zoho" deal-id={deal.deal_id} className="nasButton" onClick={openZoho} /></button>
                <button><img src={finderLogo} path={deal.path} deal-id={deal.deal_id} alt="Finder" className="nasButton" onClick={openFinderDupe} /></button>
              </div>
            ))}
        </div>
      </div>
    )
  } else if (findNasFolders.length > 0 && !loading) {
    return (
      <div className="nas_content">
        <span ref={selectionRef}/>
        <span ref={mainRef}/>
        <div className="title" style={{backgroundColor:"#701616"}}>
          <span>Couldn't Find These NAS Folders</span>
          <button className="bookmarkBtn" onClick={submitNas}>
            <span className="IconContainer">
              <svg viewBox="2 0 12 15" height="2em" className="icon">
                <path
                  d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425z"
                ></path>
              </svg>
            </span>
            <p className="text">Submit</p>
          </button>
        </div>
        <div className="nasFolders">
          {findNasFolders.map((folder) => (
            <NasFolder folder={folder} openZoho={openZoho} key={folder.id} setFindNasFolders={setFindNasFolders}/>
          ))}
        </div>
      </div>
    )
  } else if (fixableFiles.length > 0 && !loading) {
    return (
      <div className="nas_content">
        <span ref={selectionRef}/>
        <span ref={mainRef}/>
        <div className="title" style={{backgroundColor:"#3c476a"}}>
          <span>Fix These Files</span>
          <button className="bookmarkBtn" onClick={fixed}>
            <span className="IconContainer">
              <svg viewBox="2 0 12 15" height="2em" className="icon">
                <path
                  d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425z"
                ></path>
              </svg>
            </span>
            <p className="text">Submit</p>
          </button>
        </div>
        <div className="nasFolders">
          {fixableFiles.map((folder) => (
            <div className="nasFolder" >
              <div className="name" style={{width:"70%"}}>{folder.deal_name}</div>
              <button><img src={indesignLogo} alt="InDesign" deal-id={folder.deal_id} className="nasButton" onClick={openInDesign} /></button>
              <button><img src={finderLogo} deal-id={folder.deal_id} alt="Finder" className="nasButton" onClick={openFinderFix} /></button>
              <button><img src={zohoLogo} deal-id={folder.deal_id} alt="Zoho" className="nasButton" onClick={openZoho} /></button>
            </div>
          ))}
        </div>
      </div>
    )
  } else if (approved.length > 0 && !loading) {
    return (
      <div className="nas_content">
        <span ref={selectionRef}/>
        <span ref={mainRef}/>
        <div className="title" style={{backgroundColor:"rgb(69 154 74)"}}>
          <span>Send These Files</span>
          <button className="bookmarkBtn" onClick={approve}>
            <span className="IconContainer">
              <svg viewBox="2 0 12 15" height="2em" className="icon">
                <path
                  d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425z"
                ></path>
              </svg>
            </span>
            <p className="text">Submit</p>
          </button>
        </div>
        <div id="approvalCountsContainer">
          <div id="approvalCounts">
            <div className="approvalCountTile">
              <span style={{background: "#dd6edc"}} className="approvalTitle">NORMAL</span>
              <span className="approvalCount">{approved.filter(deal => deal.approval_type === "Normal").length}</span>
            </div>
            <div className="approvalCountTile">
              <span style={{background: "#60e8e4"}} className="approvalTitle">RUSHED</span>
              <span className="approvalCount">{approved.filter(deal => deal.approval_type === "Rushed").length}</span>
            </div>
            <div className="approvalCountTile">
              <span style={{background: "#f8b977"}} className="approvalTitle">ABD</span>
              <span className="approvalCount">{approved.filter(deal => deal.approval_type === "ABD").length}</span>
            </div>
          </div>
          {emailLoadingPercentage.loading === "True" ? <>
            <div id="emailLoadingBarContainer">
              <div style={{width: ((emailLoadingPercentage["Normal"].count / emailLoadingPercentage["Normal"].total) * emailLoadingPercentage["Normal"].percentage).toString() + "%",background: "#dd6edc"}} className="emailLoadingBar"></div>
              <div style={{width: ((emailLoadingPercentage["Rushed"].count / emailLoadingPercentage["Rushed"].total) * emailLoadingPercentage["Rushed"].percentage).toString() + "%",background: "#60e8e4"}} className="emailLoadingBar"></div>
              <div style={{width: ((emailLoadingPercentage["ABD"].count / emailLoadingPercentage["ABD"].total) * emailLoadingPercentage["ABD"].percentage).toString() + "%",background: "#f8b977"}} className="emailLoadingBar"></div>
            </div>
          </> : null}
          <button id='submitApprovalButton' className='button' onClick={sendEmails}>Submit</button>
        </div>
      </div>
    )
  } else if (rejected.length > 0 && !loading) {
    return (
      <div className="nas_content">
        <span ref={selectionRef}/>
        <span ref={mainRef}/>
        {errorDetails.invoice ? <span key={errorDetails.message_id} id="errorModal">Error with {errorDetails.invoice}: {errorDetails.error}</span> : null}
        {successDetails.invoice ? <span key={successDetails.message_id} id="successModal">{successDetails.invoice} went through!</span> : null}
        <div className="title" style={{backgroundColor:"rgb(204 60 193)"}}>
          <span>Rejected Files</span>
          <button className="bookmarkBtn" onClick={reject}>
            <span className="IconContainer">
              <svg viewBox="2 0 12 15" height="2em" className="icon">
                <path
                  d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425z"
                ></path>
              </svg>
            </span>
            <p className="text">Submit</p>
          </button>
        </div>
        <div className="nasFolders">
          {rejected.map((deal) => (<>
            {deal.code ? 
            <div className="nasFolder" style={{"justifyContent":"space-around"}}>
              <div className="name" style={{"width":"40%"}}>{deal.deal_name}</div>
              <div className="name" style={{"width":"25%"}}>{deal.error}</div>
              <button><img src={mailLogo} alt="Email" deal-id={deal.deal_id} className="nasButton" onClick={sendEmail} /></button>
              <button><img src={finderLogo} alt="Finder" deal-id={deal.deal_id} className="nasButton" onClick={openFinderApprove} /></button>
              <button><img src={zohoLogo} alt="Zoho" deal-id={deal.deal_id} className="nasButton" onClick={openZoho} /></button>
            </div>
            :
            <div className="nasFolder" style={{"justifyContent":"space-around"}}>
              <div className="name" style={{"width":"85%"}}>{deal.deal_name}</div>
              <button><img src={zohoLogo} alt="Zoho" deal-id={deal.deal_id} className="nasButton" onClick={openZoho} /></button>
            </div>}
          </>))}
        </div>
      </div>
    )
  } else {
    return (
      <div id="content" ref={mainRef}>
        <div id="main">
          <div className="hidden" ref={selectionRef}>
            <div id="options">
              <div id="selectionContainer" className='action-buttons'>
                <button id="clearFiles" className='button' onClick={clearFiles}>Clear</button>
                <button id="submitAssignments" className='button' onClick={submitFiles}>Submit</button>
              </div>
              <div className="cancelButton"><button className="button" onClick={cancelFinished}>Cancel</button></div>
            </div>
          </div>
          {allInvoices.length > 0 && dealInfo ? <div id='initialZoho'>
            <div className="labeledButton">
              <h2>Deal</h2>
              <img src={zohoLogo} alt="Zoho" deal-id={dealInfo.deal_id} className="nasButton" onClick={openZoho} />
            </div>
            {dealInfo.print_job_id !== "" ? <div className='labeledButton'>
              <h2>PJ</h2>
              <img src={zohoLogo} alt="Zoho" print-job-id={dealInfo.print_job_id} className="nasButton" onClick={openPrintJobZoho} />
            </div> : null}
          </div> : null}
          {allInvoices.length > 0 ? <div id="dealCounter">
            <div className="position">
              <span>{(index + 1).toString()}</span>
            </div>
            <div className="total">
              <span>{allInvoices.length.toString()}</span>
            </div>
          </div> : null}
          <div className="button-container">
            {allInvoices.length > 0 ? <button className='navButton' onClick={previousFile}><img id='previous' src={nextIcon} alt="" /></button> : <span/>}
            {allInvoices.length === 0 ? <button id="fileButton" className='button' onClick={() => {
              window.pywebview.api.find_file()
            }}><span className="text">Find File</span></button> : <button id="finishButton" className='button' onClick={showOptions}><span className="text">Finished</span></button>}
            {allInvoices.length > 0 ? <button className='navButton' onClick={nextFile}><img id='next' src={nextIcon} alt="" /></button> : <span/>}
          </div>
          {loading ? <div id="loadingRings">
            <div id='orangeCircle' className='loading'>
              <img src={orangeCircle} alt="" />
            </div>
            <div id='whiteHoop' className='loading'>
              <img src={whiteHoop} alt="" />
            </div>
            <div id='blackHoop' className='loading'>
              <img src={blackHoop} alt="" />
            </div>
          </div> : null}
          <div className="dealInfo-container">
            {dealInfo ? <DealInfo dealInfo={dealInfo} loading={loading}/> : null}
          </div>
          
          <div className="infoBar">
            <div className="allButtons">
              <div className="buttonArea">
                  <div className='slider'>
                    {stages.map((stage) => (
                      <div name={stage} className={activeStage === stage ? "stageOption selected" : "stageOption"} onClick={selectStageOption}><span>{stage.toUpperCase()}</span></div>
                    ))}
                  </div>
                  <div className='slider'>
                    {approvalStages.map((stage) => (
                      <div name={stage} className={activeApprovalStage === stage ? "stageOption selected" : "stageOption"} onClick={selectApprovalStageOption}><span>{stage.toUpperCase()}</span></div>
                    ))}
                  </div>
              </div>
              <div className="additionalButtons">
                <div id="attachmentButtonField">
                  <button id="attachmentButton" className='button' onClick={showAttachments}>Download<br/>Attachments</button>
                </div>
                <button id='acceptButton' className='button' onClick={submitProof}>Submit</button>
              </div>
            </div>
            <div className="infoFields">
              {dealInfo ? <>
                <div id="leftFields" className='fieldCategory'>
                  <div className="infoField">
                    <div className="fieldLabel">Deal Name</div>
                    <div className="fieldValue"><span>{dealInfo.deal_name.toString()}</span></div>
                  </div>
                  <div className="infoField">
                    <div className="fieldLabel">Product Type</div>
                    <div className="fieldValue"><span>{dealInfo.product_type.toString()}</span></div>
                  </div>
                </div>
                <div id='middleFields' className="fieldCategory">
                  <div className="infoField">
                    <div className="fieldLabel">Stage</div>
                    <div className="fieldValue"><span>{dealInfo.stage.toString()}</span></div>
                  </div>
                  <div className="infoField">
                    <div className="fieldLabel">Ad Size</div>
                    <div className="fieldValue"><span>{dealInfo.ad_size.toString()}</span></div>
                  </div>
                </div>
                <div id='rightFields' className="fieldCategory">
                  <div id='specialInstructions' className="infoField">
                    <div className="fieldLabel">Special Instructions</div>
                    <div id='specialInstructions' className="fieldValue"><span>{dealInfo.special_instructions.toString()}</span></div>
                  </div>
                </div>
              </> : null}
            </div>
          </div>
        </div>
        <div id="drawer" ref={drawerRef}>
          {allInvoices[index] in attachmentObject ? attachmentObject[allInvoices[index]].map((attachment) => (
            <img src={attachment} alt="" />
          )) : null}
        </div>
      </div>
    )
  }
}