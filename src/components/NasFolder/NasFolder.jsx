import { useState } from 'react'
import zohoLogo from '../../assets/zoho_icon.png'

export default function NasFolder({folder,openZoho,setFindNasFolders}) {
  const [inputValue,setInputValue] = useState(folder.nas_name)
  const [editing,setEditing] = useState(false)

  const handleChange = (e) => {
    setInputValue(e.target.value)
    setEditing(true)
  }

  const submitChange = () => {
    setFindNasFolders(folders => {
      var thisFolder = {...folder,"nas_name":inputValue}
      var updatedFolders = [...folders]
      updatedFolders.splice(folders.indexOf(folder),1,thisFolder)
      return updatedFolders
    })
    setEditing(false)
  }

  return (
    <div className="nasFolder">
      <div className="dealName">{folder.deal_name}</div>
      {/* <div className="courseName" onClick={pasteClipboard}>{pasteBoard}</div> */}
      <div className="courseName">
        <input type="text" className="courseInput" value={inputValue} onChange={handleChange}/>
        {editing ? <span className="IconContainer" onClick={submitChange}>
          <svg viewBox="2 0 12 15" height="1.5em" className="icon">
            <path
              d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425z"
            ></path>
          </svg>
        </span> : null}
      </div>
      <button><img src={zohoLogo} alt="" deal-id={folder.deal_id} className="nasButton" onClick={openZoho} /></button>
    </div>
  )
}
