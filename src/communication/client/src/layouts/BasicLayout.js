import React, {Component} from "react";
import TopNavBar from "./TopNavBar";
import PropTypes from "prop-types";
import ToolNavBar from "./ToolNavBar";
import {MDBCol, MDBContainer, MDBRow, MDBFooter} from "mdbreact";
import SearchByCategoryBox from "../components/SearchByCategoryBox";

export class BasicLayout extends Component {


    render() {
        const mainComponent = this.props.mainComponent;
        const secondaryComponent = this.props.secondaryComponent;
        const isAdmin = this.props.isAdmin.bind(this);
        const isLoggedIn = this.props.isLoggedIn.bind(this);
        const getUserName = this.props.getUserName.bind(this);
        return (
            <React.Fragment>
                <MDBContainer fluid style={{padding: "0px"}}>
                    <MDBRow>
                        <TopNavBar getUserId={this.props.getUserId} updateParent={this.props.updateParent} fe style={defaultPaddingStyle} isAdmin={isAdmin} isLoggedIn={isLoggedIn}
                                   getUserName={getUserName}/>
                    </MDBRow>
                    <MDBRow center>
                        <MDBContainer fluid>
                            <ToolNavBar isLoggedIn={isLoggedIn} isAdmin={isAdmin}/>
                        </MDBContainer>
                    </MDBRow>
                    <MDBRow style={{padding: "0.25px"}}>
                        <MDBCol size={'secondSize' in this.props ? 12-this.props.secondSize : 10}>
                            {mainComponent}
                        </MDBCol>

                        <MDBCol size={'secondSize' in this.props ? this.props.secondSize : 2}>
                            {secondaryComponent}
                        </MDBCol>
                    </MDBRow>
                    <MDBFooter color="default-color" className="font-small pt-4 mt-4 fixed-bottom">
                        <div className="footer-copyright text-center py-3">
                            <MDBContainer fluid>
                                &copy; {new Date().getFullYear()} Copyright: <a href="https://github.com/fedida/Work_Shop_On_Software_Engineering"> Project Page </a>
                            </MDBContainer>
                        </div>
                    </MDBFooter>
                </MDBContainer>
            </React.Fragment>
        );
    }
}

const defaultPaddingStyle = {
    padding: "10px",
};

// PropTypes
BasicLayout.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,
    mainComponent: PropTypes.object.isRequired,
    secondaryComponent: PropTypes.object.isRequired,
};

export default BasicLayout;
