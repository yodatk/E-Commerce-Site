import React, {Component} from "react";
import {MDBContainer, MDBRow} from "mdbreact";
import PropTypes from "prop-types";

export class OnlyHeaderComponent extends Component {
    render() {
        return (
            <MDBContainer>
                <MDBRow style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                }}>
                    <h1>{this.props.header}</h1>
                </MDBRow>
            </MDBContainer>
        );
    }
}


// PropTypes
OnlyHeaderComponent.propTypes = {
    header: PropTypes.string.isRequired
};

export default OnlyHeaderComponent;