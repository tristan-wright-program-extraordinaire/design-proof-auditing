import { useState } from 'react'
import zohoLogo from '../../assets/zoho_icon.png'
import finderLogo from '../../assets/finder_icon.png'

export default function Approved({deal,openZoho,openFinder}) {
  const [complete,setComplete] = useState(false)

  const handleChange = () => {
    setComplete(pastState => {
      return !pastState
    })
  }

  return (
    <div className="nasFolder" >
      <div className={complete ? "approvedName complete" : "approvedName"}>
        <span>{deal.deal_name}</span>
        <div className="checkbox" onClick={handleChange}>
          {complete ? <svg viewBox="2 0 12 15" height="2em" className="icon">
            <path
              d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425z"
            ></path>
          </svg> : null}
        </div>
      </div>
      <button><img src={zohoLogo} alt="" deal-id={deal.deal_id} className="nasButton" onClick={openZoho} /></button>
      <button><img src={finderLogo} deal-id={deal.deal_id} alt="Finder" className="nasButton" onClick={openFinder} /></button>
    </div>
  )
}
